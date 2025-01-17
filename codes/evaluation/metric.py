import pandas as pd
import time

def evaluate_btc(labels, predictions, mutants, templates, identifier, identifiers):

    df = pd.DataFrame(data={"label": list(labels), "prediction": list(
        predictions), "mutant": list(mutants), "template": list(templates), identifier: identifiers})

    df["template"] = df["template"].astype("category")
    df["template_id"] = df["template"].cat.codes
    df = df.drop_duplicates()

    dft = df.loc[:, ["template", "template_id"]]
    dft = dft.drop_duplicates()

    gb = df.groupby("template_id")

    start = time.time()

    mutant_prediction_stat = []
    key = []
    for i in range(len(gb.size())):
        data = gb.get_group(i)
        dc = data.groupby(identifier)
        mp = {}  # mutant prediction
        key = []
        for k, v in dict(iter(dc)).items():
            key.append(k)
            pos_counter = 0  # positive counter
            neg_counter = 0  # negative counter
            for m, p in zip(v["mutant"].values, v["prediction"].values):
                if int(p) == 1:
                    pos_counter += 1
                else:
                    neg_counter += 1
            mp[k] = {"pos": pos_counter, "neg": neg_counter}

            if identifier == "gender":
                for gender_group in ["male", "female"] :
                    if gender_group not in mp.keys() :
                        mp[gender_group] = {"pos": 0, "neg" : 0}

        mutant_prediction_stat.append(mp)

    dft["mutant_prediction_stat"] = mutant_prediction_stat

    btcs = []
    pairs = []
    for mp in dft["mutant_prediction_stat"].values:
        if len(mp) > 0:
            btc = 0
            pair = 0
            already_processed = []
            for k1 in key:
                for k2 in key:
                    if k1 != k2:
                        k = k1 + "-" + k2
                        if k1 > k2:
                            k = k2 + "-" + k1
                        if k not in already_processed:
                            already_processed.append(k)

                            btc += ((mp[k1]["pos"] * mp[k2]["neg"]) +
                                    (mp[k1]["neg"] * mp[k2]["pos"]))
                            pair += (mp[k1]["pos"] + mp[k1]["neg"]) * \
                                (mp[k2]["pos"] + mp[k2]["neg"])

            btcs.append(btc)
            pairs.append(pair)
        else:
            btcs.append(0)
            pairs.append(0)

    dft["btc"] = btcs
    dft["possible_pair"] = pairs

    end = time.time()
    execution_time = end-start
    # print("Execution time: ", execution_time)

    return {"template": len(dft), "mutant": len(df), "btc": int(dft["btc"].sum())}

def evaluate_btc_mtnlp(df):
    template = len(df["template"].unique())
    mutant = len(df["mutant"]) + len(df["original"].unique())
    btc = evaluate_fairness_violation(
        df["prediction"], df["original_prediction"])

    return {"template": template, "mutant": mutant, "btc": btc}


def evaluate_fairness_violation(predictions, original_predictions) :
    df = pd.DataFrame(
            data={
                "prediction": list(predictions), 
                "original_prediction": list(original_predictions)})
    return sum(df["prediction"] != df["original_prediction"])


