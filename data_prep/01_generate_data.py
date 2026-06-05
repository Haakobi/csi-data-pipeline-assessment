import pandas as pd
import numpy as np
import os

def generate_exact_csi_survey(num_rows=250):
    np.random.seed(42)
    data = [] # Fixed: Initialized empty list

    # --- Exact Armenian Strings from Images ---
    # Fixed: Populated 14 mock reasons to match the S4.4 loop logic
    s3_reasons = [
        "1. Նոր հեռախոսահամարի ձեռքբերում",
        "2. SIM քարտի վերականգնում / փոխարինում",
        "3. Սակագնային փաթեթի փոփոխություն",
        "4. Ինտերնետ փաթեթի ակտիվացում",
        "5. Հաշվի լիցքավորում / Վճարում",
        "6. Տեղեկատվության ստացում ծառայությունների վերաբերյալ",
        "7. Բողոք / Դժգոհություն",
        "8. Ռոումինգի ակտիվացում / ապաակտիվացում",
        "9. Հեռախոսի կամ աքսեսուարի գնում",
        "10. Ապառիկ վաճառքի ձևակերպում",
        "11. Տեխնիկական աջակցություն / Խնդիրների լուծում",
        "12. Պայմանագրի խզում",
        "13. Համարի տեղափոխում (MNP)",
        "14. Այլ հարցեր"
    ]

    q4_5_sub_reasons = [
        "Աշխատակցի սպասարկման որակի պատճառով",
        "Այս գրասենյակում նման ծառայություններ չեն տրամադրվում",
        "Գրասենյակում առկա երկար հերթը",
        "Չկարողացա լուծել իմ խնդիրը, քանի որ ես չէի ներկայացրել անհրաժեշտ փաստաթղթեր / իմ հեռախոսը չուներ համապատասխան տեխնիկական պարամետրեր / այլ պատճառով, որը կախված էր իմ գործողություններից",
        "Տեխնիկական խնդիր, որն առկա էր սպասարկման կենտրոնում/համապատասխան մասնագետի բացակայություն",
        "Դժվարանում եմ պատասխանել",
        "Այլ, խնդրում ենք նշել"
    ]

    # Fixed: Populated mobile operators in Armenia
    operators = ["Viva", "Ucom", "Team Telecom"]

    for i in range(1, num_rows + 1):
        row = {}

        # 1. Base Setup 
        row["Օպերատոր"] = np.random.choice(operators) # Fixed: Added column key
        row["Հասցե"] = "Վանաձոր 1 - Տիգրան Մեծ 75"
        row["Ներկայացեք՝ Բարև Ձեզ, իմ անունը...... է: Ես «Ի-Վի» հետազոտական ընկերությունից եմ..."] = f"Resp_{i}"
        row["Հարցազրուցավար"] = np.random.choice(["Հարցազրուցավար_1", "Հարցազրուցավար_2", "Հարցազրուցավար_3"])

        # 2. S3 Block
        s3_prefix = "S3. Դուք քիչ առաջ այցելել եք ______ (Նշել օպերատորի անունը) բաժանորդների սպասարկման կենտրոն: Ո՞րն է եղել Ձեր այցելության նպատակը (Նշել 2 հիմնական պատասխան):/"

        active_s3_indices = [] # Fixed: Initialized empty list
        for idx, reason in enumerate(s3_reasons, 1):
            val = np.random.choice([1, 0], p=[0.1, 0.9]) # Fixed: Added choices [1, 0]
            row[f"{s3_prefix}{reason}"] = val
            if val == 1:
                active_s3_indices.append(idx)

        row["Այլ (նշել)"] = np.nan
        # Removed syntax error: `row = np.nan`

        # 3. S4.4 Block
        s4_4_prefix = "S4.4 Ձեզ հարցումը լուծել այն հարցը, ինչի համար եկել էիք բաժանորդների սպասարկման կենտրոն: Խոսքը վերաբերում է միայն այս այցելությանը: (ԿԱՐԴԱՑԵՔ ՅՈՒՐԱՔԱՆՉՅՈՒՐ S3-ՈՒՄ ՆՇՎԱԾ ՊԱՏԱՍԽԱՆԻ ՀԱՄԱՐ: ՆՇԵԼ S3-ՈՒՄ ՆՇՎԱԾ ԱՅՑԻ ՆՊԱՏԱԿԻ ՄՈԴԵԼԸ ԵՎ ՊԱՏԱՍԽԱՆԸ)"
        row[s4_4_prefix] = np.nan

        for idx, reason in enumerate(s3_reasons, 1):
            if idx <= 14:
                reason_clean_name = reason.split('. ', 1)[1] if '. ' in reason else reason
                col_name = f"S4.4_{idx}. {reason_clean_name}"
                row[col_name] = "Այո" if idx in active_s3_indices else np.nan

        # 4. Massive 4.5 Block
        row["4.5 Ինչո՞ւ եք պատասխանել, որ Ձեր հարցը լուծված չէ (նշել 1 պատասխան)"] = np.nan

        for idx, reason in enumerate(s3_reasons, 1):
            if idx <= 14:
                reason_clean_name = reason.split('. ', 1)[1] if '. ' in reason else reason
                for sub_reason in q4_5_sub_reasons:
                    col_name = f"4.5_{idx} {reason_clean_name}/{sub_reason}"
                    if idx in active_s3_indices:
                        row[col_name] = np.random.choice([1, 0, np.nan], p=[0.2, 0.2, 0.6])
                    else:
                        row[col_name] = np.nan

        # 5. Satisfaction & Correlation Columns (A2-A4 and 5.1-5.12)
        row["A2. Ընդհանուր առմամբ որքանո՞վ եք բավարարված այս սպասարկման կենտրոնի գործունեությունից՝ այն այցելելուց հետո։ Գնահատեք 10 բալային սանդղակով, որտեղ “1”-ը նշանակում է «ընդհանրապես բավարարված չեմ», իսկ “10”-ը՝ «միանգամայն բավարարված եմ»։"] = np.random.randint(5, 11)
        row["A3. Ընդհանուր առմամբ որքանո՞վ է համապատասխանում Ձեր ակնկալիքներին այս սպասարկման կենտրոնի աշխատանքի որակը։"] = np.random.randint(5, 11)
        row["A4. Ընդհանուր առմամբ, այս սպասարկման կենտրոնը որքանո՞վ է համապատասխանում հաճախորդների սպասարկման «իդեալական» կենտրոնի վերաբերյալ Ձեր պատկերացումներին: Գնահատեք 10 բալային սանդղակով"] = np.random.randint(4, 11)
        
        row["5.1 Աշխատակիցների բարեհամբույր վերաբերմունքը"] = np.random.randint(5, 11)
        row["5.2 Աշխատակիցների արտաքինը"] = np.random.randint(6, 11)
        row["5.3 Աշխատակիցների օգնելու պատրաստակամությունը, հաճախորդի նկատմամբ հետաքրքրվածությունը"] = np.random.randint(5, 11)
        row["5.4 Հարցերի պատասխանների հասկանալիությունը"] = np.random.randint(5, 11)
        row["5.5 Հերթերի ծանրաբեռնվածություն"] = np.random.randint(4, 11)
        row["5.6 Սպասելու հարմարավետությունը"] = np.random.randint(5, 11)
        row["5.7 Ձեր հարցերի լուծման արագությունն ու արդյունավետությունը"] = np.random.randint(4, 11)
        row["5.8 Բավարարվածությունը Ձեր խնդրի լուծման արդյունքից"] = np.random.randint(5, 11)
        row["5.9 Սպասարկման կենտրոնի կոկիկությունը, ձևավորումը (հաճելի է գտնվել այնտեղ)"] = np.random.randint(6, 11)
        row["5.10 Սպասարկման կենտրոնի տարածքը լավ է կազմակերպված (հեշտ է ինքնուրույն կողմնորոշվել)"] = np.random.randint(6, 11)
        row["5.11 Սպասարկման կենտրոնի արտաքին տեսքը (շենքից դուրս)"] = np.random.randint(6, 11)
        row["5.12 Սպասարկման կենտրոնի տեղանքի /գտնվելու վայրի/ հարմարավետությունը"] = np.random.randint(6, 11)

        row["A6. Ձեր կարծիքով այս սպասարկման կենտրոնի սպասարկման որակը..."] = str(np.random.randint(1, 6))
        row["A7. Ըստ Ձեզ այս սպասարկման կենտրոնը կարիք ունի՞ բարելավելու իր գործունեությունը (նշել տարբերակները) /Ոչ (անցնել հարց A8)"] = np.random.choice(["1 Այո", "2 Ոչ"])
        row["A7.1 Կանկարագրե՞ք ինչը պետք է բարելավվի սպասարկման կենտրոնի գործունեության մեջ"] = np.nan

        # 6. Demographics and Sub-routing
        row["A8. Հաճախ եք այցելում այս սպասարկման կենտրոն:"] = np.random.choice(["1 Այո (Անցնել հարց 9.2-ին)", "2 Ոչ (Անցնել հարց 10.1-ին)"])
        
        # Fixed: Added valid choice options for prepaid/postpaid logic
        is_prepaid = np.random.choice([1, 0])
        row["9.1 Դուք ներկայանում հանդիսանում եք ------ բջջային օպերատորի անունը, որի սպասարկման կենտրոնի մոտ անցկացվում է հարցումը/ բաժանորդ /1 Կանխավճարային"] = is_prepaid
        row["9.1 Դուք ներկայանում հանդիսանում եք ------ բջջային օպերատորի անունը, որի սպասարկման կենտրոնի մոտ անցկացվում է հարցումը/ բաժանորդ /2 Հետվճարային"] = 1 - is_prepaid
        
        row["9.2 ------ բջջային օպերատորի անունը, որի սպասարկման կենտրոնի մոտ անցկացվում է հարցումը/ ինչ քարտից / փաթեթից եք օգտվում /կորպորատիվ / բիզնես"] = 0
        row["9.2 ------ բջջային օպերատորի անունը... /Այլ"] = 0
        row["Հարց 10.1 Իսկ սա Ձեր միակ օպերատորն է, թե՞ այլ օպերատորների ծառայություններից ևս օգտվում եք/ունեք ակտիվ քարտեր:"] = "0 Միակ օպերատորն է"
        row["Հարց 10.2 Իսկ ո՞ր օպերատորի/օպերատորների ծառայություններից եք օգտվում:"] = np.nan
        row["Հարց 10.3 Բջջային կապի վրա կատարվող ամսական ծախսը (թույլատրվում է միայն մեկ պատասխան)"] = np.random.choice(["Մինչև 2,000 դրամ", "2,001-3,000 դրամ", "3,001-5,000 դրամ"])
        row["10.5 Տարիք"] = np.random.choice(["18-24 տարեկան", "31-40 տարեկան"])

        # 7. System Columns
        row["_notes"] = np.nan
        row["_status"] = "submitted_via_web"
        row["_submitted_by"] = f"vBF8dHIxKidF9PsTeEcNzh{np.random.randint(100,999)}"
        row["_version_"] = np.nan
        row["_tags"] = np.nan
        row["_index"] = i
        row["Label"] = i

        data.append(row)

    df = pd.DataFrame(data)
    
    # Create data directory if it doesn't exist to prevent path errors
    os.makedirs("data", exist_ok=True)
    
    # Save the file to the data/ folder for GitHub
    with pd.ExcelWriter("data/csi_database.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Database Start", index=False)
    
    # Fixed: Corrected shape output syntax so it shows Rows by Columns
    print(f"Dataset generated successfully! Shape: {df.shape[0]} rows by {df.shape[1]} columns.")

if __name__ == "__main__":
    generate_exact_csi_survey()
