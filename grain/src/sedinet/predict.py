import json, os
from numpy import any as npany
import json

BASE_PATH = "/app/src/sedinet"

CONFIG_PATH = f"{BASE_PATH}/config/config_sandsnap_70_30.json"
WEIGHTS_PATH = [
    f"{BASE_PATH}/res/sandsnap/sandsnap_70_30_simo_batch12_im512_512_9vars_pinball_noaug.weights.h5",
    f"{BASE_PATH}/res/sandsnap/sandsnap_70_30_simo_batch14_im512_512_9vars_pinball_noaug.weights.h5",
]

USE_GPU = True

if USE_GPU == True:
    ##use the first available GPU
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"  #'1'
else:
    ## to use the CPU (not recommended):
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


# load the user configs
def load_config(config_path):
    with open(config_path) as f:
        config = json.load(f)

    csvfile = config["csvfile"]
    res_folder = config["res_folder"]
    name = config["name"]
    dropout = config["dropout"]
    scale = config["scale"]
    greyscale = config["greyscale"]

    try:
        numclass = config["numclass"]
    except:
        numclass = 0

    try:
        greyscale = config["greyscale"]
    except:
        greyscale = "true"

    vars = [
        k
        for k in config.keys()
        if not npany(
            [
                k.startswith("base"),
                k.startswith("MAX_LR"),
                k.startswith("MIN_LR"),
                k.startswith("DO_AUG"),
                k.startswith("SHALLOW"),
                k.startswith("res_folder"),
                k.startswith("train_csvfile"),
                k.startswith("csvfile"),
                k.startswith("test_csvfile"),
                k.startswith("name"),
                k.startswith("greyscale"),
                k.startswith("aux_in"),
                k.startswith("dropout"),
                k.startswith("N"),
                k.startswith("scale"),
                k.startswith("numclass"),
            ]
        )
    ]
    vars = sorted(vars)

    if len(vars) == 1:
        mode = "siso"
    elif len(vars) > 1:
        mode = "simo"

    return vars, greyscale, dropout, scale


from .sedinet_models import *

SM = None
CS = None


def load_model(vars, greyscale, dropout, scale, weights_path):
    global SM, CS
    if type(BATCH_SIZE) == list:
        SM = []
        for batch_size, valid_batch_size, wp in zip(
            BATCH_SIZE, VALID_BATCH_SIZE, weights_path
        ):
            sm = make_sedinet_siso_simo(vars, greyscale, dropout)
            sm.load_weights(wp)
            SM.append(sm)

    else:
        if isinstance(weights_path, list):
            weights_path = weights_path[0]
        SM = make_sedinet_siso_simo(vars, greyscale, dropout)

    if scale == True:
        CS = joblib.load(weights_path.replace(".weights.h5", "_scaler.pkl"))
    else:
        CS = []

    if type(SM) == list:
        try:
            counter = 0
            for s, wp in zip(SM, weights_path):
                exec("s.load_weights(os.getcwd()+os.sep+wp)")
            counter += 1
        except:
            counter = 0
            for s, wp in zip(SM, weights_path):
                exec("s.load_weights(wp)")
            counter += 1
    else:
        try:
            SM.load_weights(os.getcwd() + os.sep + weights_path)
        except:
            SM.load_weights(weights_path)


def estimate_siso_simo(
    image,
    greyscale,
    scale,
    weights_path,
):
    """
    This function uses a sedinet model for continuous prediction on 1 image
    """
    im = Image.fromarray(image)

    if greyscale == True:
        im = im.convert("LA")
        im = im.resize((IM_HEIGHT, IM_HEIGHT))
        im = np.array(im)[:, :, 0]
    else:
        im = im.resize((IM_HEIGHT, IM_HEIGHT))
        im = np.array(im)

    im = np.array(im) / 255.0

    if greyscale == True:
        if type(SM) == list:
            R = []
            for s in SM:
                R.append(s.predict(np.expand_dims(np.expand_dims(im, axis=2), axis=0)))
            result = np.median(np.hstack(R), axis=1)
            del R
        else:
            result = SM.predict(np.expand_dims(np.expand_dims(im, axis=2), axis=0))
    else:
        # result = SM.predict(np.expand_dims(im, axis=0))
        if type(SM) == list:
            R = []
            for s in SM:
                R.append(s.predict(np.expand_dims(im, axis=0)))
            result = np.median(np.hstack(R), axis=1)
            del R
        else:
            result = SM.predict(np.expand_dims(im, axis=0))

    result = [float(r[0]) for r in result]

    if scale == True:
        result_scaled = []
        for r, cs in zip(result, CS):
            result_scaled.append(
                float(cs.inverse_transform(np.array(r).reshape(1, -1))[0])
            )
        del result
        result = result_scaled

    if type(SM) == list:
        # files = glob(os.path.dirname(weights_path[0])+os.sep+'*.pkl') #.replace('.hdf5','_bias.pkl')
        # file = [f for f in files if '_'.join(np.asarray(BATCH_SIZE, dtype='str')) in f][0]
        # Z = joblib.load(file)
        # Z = []
        # for wp in weights_path:
        #     Z.append(joblib.load(wp.replace('.weights.h5','_bias.pkl')))
        pass
    else:
        bias_path = weights_path.replace(".weights.h5", "_bias.pkl")
        if os.path.exists(bias_path):
            Z = joblib.load(bias_path)

            result_scaled = []
            for z, r in zip(Z, result):
                result_scaled.append(np.abs(np.polyval(z, r)))
            del result
            result = result_scaled
        else:
            print(
                f"Warning: Bias file not found at {bias_path}. Skipping bias correction."
            )

    return result


vars, greyscale, dropout, scale = load_config(CONFIG_PATH)

load_model(vars, greyscale, dropout, scale, WEIGHTS_PATH)


def predict_grain_size(image):
    prediction = estimate_siso_simo(
        image,
        greyscale,
        scale,
        WEIGHTS_PATH,
    )
    return prediction
