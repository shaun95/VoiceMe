from tqdm import tqdm

import requests
import json
import base64
from glob import glob
from os.path import basename
from os import makedirs
import tempfile

STYLES = {
    "OR":[[-0.43749552965164185,0.07102394104003906,-0.5458381772041321],[0.37267372012138367,-0.3017159402370453,-0.41550102829933167],[0.24301443994045258,-0.3958871364593506,-0.3180898427963257],[0.1233600601553917,-0.23055370151996613,-0.10752342641353607],[0.8576979637145996,-0.37379831075668335,0.677169919013977],[0.8185730576515198,-0.18993748724460602,0.512082576751709],[0,0,0],[0.10421077907085419,-0.3326321542263031,0.330244779586792],[0.7550053596496582,-0.41693106293678284,0.18334949016571045],[0,0,0],[0.2143217921257019,0.04454510286450386,-0.2726135849952698],[0,0,0],[0.7677611112594604,0.15605208277702332,0.2504274547100067],[0.9453743696212769,0.1873970329761505,-0.03926842659711838],[0.3195790946483612,-0.22831031680107117,-0.2735641300678253],[0,0,0],[-0.7701455354690552,0.30647745728492737,0.7981677651405334],[0.448192298412323,-0.1356646716594696,0.4628775715827942],[0,0,0]],
    "BAO":[[-0.020465942099690437,-0.49054470658302307,-0.03396625444293022],[0.014644566923379898,0.2036738395690918,-0.7354193925857544],[-0.22365520894527435,0.34592658281326294,-0.5886687636375427],[-0.021121928468346596,-0.005758476909250021,-0.34310653805732727],[-0.0840878114104271,0.40350520610809326,-0.541016697883606],[0.25587061047554016,0.2356073558330536,-0.38141414523124695],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0.06604572385549545,0.47612977027893066,-0.7867875695228577],[0,0,0],[0.007308112923055887,0.9964383244514465,-0.5764318108558655],[0.5535326600074768,0.783237636089325,-0.6389514207839966],[-0.16436618566513062,0.21614354848861694,-0.7709344625473022],[0.12549588084220886,0.22235721349716187,-0.7613847851753235],[0.0535891130566597,0.04734647646546364,-0.6658850312232971],[0.040572937577962875,-0.414077490568161,0.15071167051792145],[0,0,0]],
    "EX0":[[-0.3593064844608307,-0.2417987585067749,-0.4355354905128479],[0.22119146585464478,0.10250049829483032,-0.8327618837356567],[-0.029717393219470978,0.1408178210258484,-0.688149094581604],[-0.9999957084655762,0.5310831665992737,-0.6465974450111389],[-0.45312222838401794,0.03423404321074486,-0.12017344683408737],[0,0,0],[0,0,0],[0.8613466024398804,0.16156010329723358,-0.6899070739746094],[0.8405997157096863,0.1199226975440979,-0.850640058517456],[0,0,0],[0.37463125586509705,-0.004257678519934416,-0.9290128946304321],[0,0,0],[-0.11374329775571823,0.4663853645324707,-0.05495736747980118],[0.7862537503242493,0.08487509936094284,-0.5197312831878662],[0.30199506878852844,0.21368208527565002,-0.7874651551246643],[0,0,0],[0,0,0],[0.6330565810203552,0.30394449830055237,0.05951186642050743],[0.43687427043914795,0.28330469131469727,-0.09091901034116745]],
    "EX3":[[-0.3522241413593292,-0.09001802653074265,0.17428943514823914],[0.03961009159684181,0.1719585359096527,-0.7799277901649475],[0.09900326281785965,0.06251280754804611,-0.5213426947593689],[-0.9982370138168335,0.5404332876205444,-0.9898694753646851],[-0.11846012622117996,0.16772809624671936,-0.005415478255599737],[0.19830046594142914,-0.045436784625053406,0.17646028101444244],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0.08667147904634476,0.3432597517967224,-0.7764228582382202],[0,0,0],[-0.052910808473825455,0.7594922184944153,-0.8033083081245422],[0.7248982787132263,0.32502681016921997,-0.807524561882019],[0.32682564854621887,-0.434313029050827,-0.46924087405204773],[0,0,0],[-0.35847780108451843,0.37646740674972534,-0.5781227946281433],[0.24362441897392273,-0.47169768810272217,0.18799056112766266],[-0.5160521864891052,0.18228383362293243,-0.18635877966880798]],
    "EX5":[[0.011229815892875195,0.04614238068461418,-0.5412487387657166],[-0.29962092638015747,-0.09517812728881836,-0.6768246293067932],[0.011446110904216766,-0.13763253390789032,-0.4904029071331024],[0.011446110904216766,-0.13763253390789032,-0.4904029071331024],[-0.6678107380867004,-0.27543264627456665,-0.13195271790027618],[-0.6678107380867004,-0.27543264627456665,-0.13195271790027618],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[-0.12181056290864944,-0.24052269756793976,-0.6731992959976196],[0,0,0],[0.11400463432073593,0.2617951035499573,-0.3647461533546448],[0.6425947546958923,-0.2331847846508026,-0.20537631213665009],[-0.3413737118244171,-0.15403041243553162,-0.5646108388900757],[0,0,0],[-0.7694098353385925,0.1200103834271431,0.15132693946361542],[0.4653029143810272,-0.1457504779100418,-0.313039094209671],[0,0,0]],
    "IM1":[[-0.07455751299858093,-0.04182128608226776,-0.3515433669090271],[-0.11963553726673126,0.05372557416558266,-0.8398405909538269],[-0.076706662774086,0.16485920548439026,-0.399036169052124],[-0.027433928102254868,-0.27781668305397034,-0.6323650479316711],[-0.3268566429615021,0.3502558767795563,-0.2672882676124573],[0.6485196352005005,0.007162511348724365,-0.7251414656639099],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[-0.0597665011882782,0.06212393194437027,-0.9199671149253845],[0,0,0],[0.17377689480781555,0.22293606400489807,-0.9041903614997864],[0.3870754539966583,0.03907592222094536,-0.9449148178100586],[-0.6870298981666565,0.004700387362390757,-0.441152960062027],[0,0,0],[-0.6707982420921326,0.22527740895748138,-0.5092217922210693],[0.14400164783000946,-0.20901240408420563,-0.01434527151286602],[0,0,0]],
    "P00":[[-0.222139373421669,0.07041000574827194,-0.1603565514087677],[0.038818079978227615,-0.10668140649795532,-0.7819315195083618],[0,0,0],[-0.05729632452130318,-0.09524121135473251,-0.18013231456279755],[0,0,0],[0.003352041356265545,-0.2424008548259735,-0.036664530634880066],[0.9631245732307434,-0.9108994007110596,-0.8486292958259583],[0.5904386043548584,-0.5154268741607666,-0.7094244360923767],[0.6892439126968384,-0.7823931574821472,-0.021960558369755745],[0,0,0],[-0.2084350883960724,-0.04979781061410904,-0.5837446451187134],[0,0,0],[-0.06679842621088028,-0.1260071098804474,-0.7018581628799438],[0.4626837372779846,-0.3167094588279724,-0.7897328734397888],[0.008855815976858139,0.04714985936880112,-0.8134766221046448],[0,0,0],[0,0,0],[0.4412403106689453,-0.416157603263855,-0.019271552562713623],[-0.045497916638851166,-0.3038177192211151,-0.2653766870498657]],
    "P04":[[0.09654528647661209,0.13043393194675446,-0.5810407996177673],[0.17331835627555847,-0.30975306034088135,-0.46545514464378357],[-0.5996229648590088,-0.19190631806850433,0.6329401731491089],[-0.29107311367988586,-0.25405117869377136,-0.046762168407440186],[-0.7558519840240479,-0.349514365196228,0.1891210526227951],[-0.43722864985466003,-0.5315755605697632,0.2556183934211731],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0.16816546022891998,-0.2376123070716858,-0.6569943428039551],[0,0,0],[0.22636660933494568,-0.3664097189903259,-0.4332844018936157],[0.2533874213695526,-0.011599724180996418,-0.30655619502067566],[-0.12891818583011627,-0.27799221873283386,-0.31500115990638733],[0,0,0],[0.17611025273799896,0.16692595183849335,-0.7070534825325012],[-0.41599351167678833,-0.32436490058898926,0.3252253830432892],[0,0,0]],
    "P06":[[0.7919741272926331,0.1009237989783287,-0.8405311107635498],[-0.565545380115509,0.14290976524353027,-0.7021436095237732],[-0.4238205552101135,0.24961993098258972,-0.6725164651870728],[-0.130369171500206,0.05558079108595848,-0.07366534322500229],[-0.44018927216529846,0.16502384841442108,0.05930579453706741],[-0.5605931878089905,0.002813066355884075,-0.004965055268257856],[0,0,0],[-0.6578773260116577,0.14002226293087006,-0.6766881346702576],[-0.08051402121782303,0.289856880903244,-0.7298961281776428],[-0.5845187902450562,0.30026957392692566,-0.37409207224845886],[-0.6358829736709595,0.11086054146289825,-0.5875905156135559],[-0.14487439393997192,0.08612703531980515,0.213863343000412],[-0.7573522925376892,0.3448127508163452,0.005378623027354479],[0.02302202396094799,-0.11495945602655411,-0.5884506106376648],[-0.5254718661308289,-0.11393139511346817,-0.12195906788110733],[0,0,0],[-0.2765898108482361,-0.36938443779945374,0.03824900463223457],[-0.35794442892074585,-0.280271053314209,0.15054813027381897],[0,0,0]],
    "RE0":[[-0.22855731844902039,-0.1699175387620926,0.1835767775774002],[-0.13510310649871826,0.026337144896388054,-0.7458192110061646],[-0.22980119287967682,0.17779897153377533,-0.24305744469165802],[-0.11538109928369522,0.0626332089304924,0.09549644589424133],[-0.10084723681211472,-0.015261356718838215,-0.2225465625524521],[-0.2877122163772583,-0.03352471441030502,-0.03467846289277077],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[-0.2389526665210724,-0.062462445348501205,-0.8288723826408386],[0,0,0],[-0.36795809864997864,0.04312712326645851,-0.4121949374675751],[0.22106176614761353,-0.26811519265174866,-0.692582368850708],[0.009286266751587391,-0.03443894907832146,-0.829373836517334],[0,0,0],[-0.04633330553770065,0.009829451330006123,-0.6321399807929993],[0.15882478654384613,-0.26272937655448914,-0.06439211964607239],[0.2970655560493469,0.04097291827201843,-0.5581880807876587]],
    "RE1":[[-0.20747043192386627,-0.38620370626449585,0.45116478204727173],[-0.02163880318403244,0.07922564446926117,-0.6709743738174438],[-0.7665700912475586,0.7996032238006592,-0.6638912558555603],[-0.2512865960597992,0.1408306211233139,-0.19842121005058289],[-0.2111186534166336,0.6882377862930298,-0.4050798714160919],[0.15421806275844574,0.06189192458987236,-0.314243346452713],[0,0,0],[0.11044994741678238,0.6447686553001404,-0.6463640332221985],[0.4739692509174347,-0.2594740390777588,-0.3884091079235077],[0,0,0],[-0.4069594442844391,0.45619726181030273,-0.5426680445671082],[-0.2848368287086487,0.7835631966590881,0.009293390437960625],[-0.2047577053308487,0.39332324266433716,-0.04965430498123169],[0.19740712642669678,0.16740716993808746,-0.3858720660209656],[0.3367365300655365,-0.6230955719947815,-0.152327761054039],[0,0,0],[0.4304367005825043,-0.25229039788246155,-0.3582225739955902],[-0.07817255705595016,-0.07743699848651886,-0.4796306788921356],[0.7800455689430237,0.3601069748401642,-0.6783447861671448]],
    "R00":[[0.037479665130376816,-0.60228031873703,0.24213452637195587],[-0.09948556125164032,0.2431497573852539,-0.7922697067260742],[-0.6022286415100098,0.665661096572876,-0.6825255155563354],[-0.3879440724849701,0.7766205668449402,-0.7153333425521851],[-0.12747377157211304,0.5902050137519836,-0.4521664083003998],[0.044032201170921326,0.7549880146980286,-0.4581071734428406],[0,0,0],[0.42343106865882874,0.49558591842651367,-0.5212398767471313],[0.3962908983230591,0.6530951857566833,-0.8543018102645874],[0,0,0],[-0.3762435019016266,0.40358567237854004,-0.6504507660865784],[0,0,0],[-0.4570900499820709,0.8508101105690002,-0.5932478904724121],[0.3740321099758148,0.6805722713470459,-0.682528555393219],[0.19306926429271698,0.1211027130484581,-0.5358322262763977],[0,0,0],[-0.10256671905517578,0.27873149514198303,-0.4428609609603882],[0.17327171564102173,-0.43554019927978516,0.1855466663837433],[0,0,0]],
    "R02":[[0.05326765403151512,-0.09693143516778946,0.3237329125404358],[-0.10951364040374756,-0.08896421641111374,-0.7912067770957947],[-0.3612121343612671,0.10946645587682724,-0.18171024322509766],[-0.10436344891786575,-0.16396582126617432,-0.25759243965148926],[-0.1241748034954071,0.23322376608848572,-0.17320258915424347],[-0.028916943818330765,0.23979651927947998,-0.06459420919418335],[0,0,0],[0,0,0],[0,0,0],[0.019258268177509308,0.1684250831604004,-0.11331993341445923],[-0.256866991519928,-0.04377007484436035,-0.7099118232727051],[0,0,0],[0.402859628200531,0.537726640701294,-0.20685432851314545],[0.8758737444877625,0.15300990641117096,-0.44788965582847595],[0.12806126475334167,-0.20627185702323914,-0.3265990912914276],[0,0,0],[-0.09054587036371231,-0.017125314101576805,-0.26066136360168457],[-0.08325423300266266,-0.023864278569817543,-0.4507915675640106],[0,0,0]],
}

for img_path in tqdm(sorted(glob('../stills/*'))):
    bname = basename(img_path)
    with tempfile.TemporaryDirectory() as out_dir:
        tmp_img = out_dir + '/' + bname
        with open(img_path, "rb") as f:
            im_bytes = f.read()
        image = base64.b64encode(im_bytes).decode("utf8")

    response = requests.post(
        'https://detect-face-fnk37ur3qq-an.a.run.app/api/v1/detect/',
        json = {'image': image}
    )

    anno_img = json.loads(response.content.decode())['data']['anno_img']

    for style_name, style in STYLES.items():
        makedirs(f'images/{style_name}', exist_ok=True)
        data = {
            "anno_img": anno_img,
            "style": style
        }
        response = requests.post(
                    'https://convert-to-art-fnk37ur3qq-an.a.run.app/api/v1/convert/',
                    json={"anno_img":anno_img,"style":style}
        )
        im_b64 = json.loads(response.content.decode())['data']['image']

        with open(f'../images/{style_name}/{bname}', "wb") as f:
            im_bytes = f.write(base64.b64decode(im_b64))