import wrds
import pandas as pd  # Import pandas for handling data

db = wrds.Connection()
ccm_lnkused = db.raw_sql("""
    SELECT ugvkey, upermno AS permno, ulinktype, ulinkprim,
           ulinkdt, ulinkenddt
    FROM crsp.ccmxpf_lnkused
""")

# Convert the result to a pandas DataFrame and save it as a CSV file
ccm_lnkused_df = pd.DataFrame(ccm_lnkused)
ccm_lnkused_df.to_csv('ccm_lnkused.csv', index=False)  # Save to a CSV file
print("Data saved to ccm_lnkused.csv")