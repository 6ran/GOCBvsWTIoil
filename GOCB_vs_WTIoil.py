import pandas as pd

#the links to these files can found in the readme section
gocb_json = r"C\...\bond_yields_marketable.json"
wti_csv =  r"C:\...\WTI_data.csv"

#JSON to Dataframe

def json_to_df(x):
    df = pd.read_json(x, typ = 'split')
    gocb_file = df.loc["observations"]

    # Create a list and then extract the values from the json file
    c1 = []
    c2 = []
    c3 = []
    c4 = []
    c5 = []

    for i in gocb_file:
        c1.append(i['d'])
        c2.append(i['CDN.AVG.1YTO3Y.AVG']['v'])
        c3.append(i['CDN.AVG.3YTO5Y.AVG']['v'])
        c4.append(i['CDN.AVG.5YTO10Y.AVG']['v'])
        c5.append(i['CDN.AVG.OVER.10.AVG']['v'])

    gocb_df = pd.DataFrame({"Date": c1, "1y-3y Avg": c2, "3y-5y Avg": c3, "5y-10y Avg": c4, "Over 10y Avg": c5})
    gocb_df['Date'] = pd.to_datetime(gocb_df.Date)
    gocb_df['Date'] = gocb_df['Date'].dt.strftime('%m/%d/%Y')

    return gocb_df


#Open CSV file and clean the data

def csv_to_df(csv_file):

    csv_df = pd.read_csv(csv_file)
    csv_df = csv_df.drop(columns=['Open','High','Low','Vol.','Change %'])
    csv_df['Date']= pd.to_datetime(csv_df['Date'], errors='coerce', utc=True).dt.strftime('%m/%d/%Y')
    csv_df = csv_df.set_index('Date')
    csv_df = csv_df.dropna(how = 'any')

    return csv_df

gocb_df = json_to_df(gocb_json)

df2 = csv_to_df(wti_csv)


#change values to float
def df_float(x):
    for j in x.filter(regex= 'Avg').columns:
        x[str(j)] = x[str(j)].astype('float')
    return x

gocb_df2 = df_float(gocb_df)

gocb_df2 = gocb_df2.set_index('Date')

gocb_df2 = gocb_df2.join(df2,how = "outer")

gocb_df2 = gocb_df2.dropna(axis=0,how = 'any')

#Grab the averages for each column and subtract them from the first column

def subtract_mean(c):
    for j in c.columns:
        gocb_mean = c[str(j)].mean()
        c[f'{j}_A'] = c[str(j)] - gocb_mean
    return c

gocb_df2 = subtract_mean(gocb_df2)

#calculation a x b and a^2
for k in gocb_df2.columns[5:9]:
    gocb_df2[f'{k}B'] = gocb_df2[str(k)] * gocb_df2['Price_A']
    gocb_df2[f'{k}2'] = gocb_df2[str(k)] ** 2

#calculation Price ^ 2
gocb_df2['Price_B2'] = gocb_df2['Price_A'] ** 2

p_corrl = []
p_var = ['1-3y','3-5y','5-10y','10+y']
p_list = []
count = 0

#filter for the a^2 columns
for l in gocb_df2.filter(regex='A2').columns:
    a2b2 = (gocb_df2[str(l)].sum() * gocb_df2['Price_B2'].sum()) ** 0.5
    p_list.append(a2b2)

#filter for the ab columns
for m in gocb_df2.filter(regex='AB'):
    p_corrl.append(gocb_df2[str(m)].sum()/p_list[count])
    count += 1

pearson_corr = dict(zip(p_var,p_corrl))

print(pearson_corr)

