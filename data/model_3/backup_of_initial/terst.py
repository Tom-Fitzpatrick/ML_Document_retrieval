import pandas as pd


dict = {
	"uni1": ["abad", "ee", "", ""],
	"uni2": ["bb", "ee'", "12r", "pop"],
	"uni3": ["x", '', '', ''],
	"uni4": ["qw", "43rw", "sdf", ""]
}

df = pd.DataFrame(dict)

print(df)

df = df.assign(uni5=pd.Series(["", "", "fuk", "weork"]).values)

print(df)

print(df.columns.tolist())
#
#
# df = pd.read_csv('found_syllabi_model3.csv')
#
# print(df)
#
# dict = df.to_dict()
#
# print(dict)

