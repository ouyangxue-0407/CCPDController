# send 
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# chat gpt's natural language processing model engine's name & key
model_engine = "gpt-3.5-turbo-instruct"
# openai.api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


# TypeError: Missing required arguments; Expected either ('messages' and 'model') or ('messages', 'model' and 'stream') arguments to be given

# convert QA record comment to inventory comment
def convertInitials(input_str: str) -> str:
    input_str = input_str.replace("UT.","UNTEST ")
    input_str = input_str.replace("MP.","MISSING PARTS ")
    input_str = input_str.replace("FT.","FUNCTION TEST ")
    input_str = input_str.replace("SI.","IMAGE SHOW SIMILAR ITEM ")
    input_str = input_str.replace("PT.","POWER TEST ")
    input_str = input_str.replace("API.","ALL PARTS IN ")
    input_str = input_str.replace("MA.","MISSING ACCESSORIES ")
    return input_str

# short description (lead on auction flex max 40 char )
def generate_short_product_title(description):
    prompt = f"You are an Auctioneer, based on the information, create a short product title. The character limit for product title is 30 byte. {description}."
    res = client.chat.completions.create(
        # model_engine=model_engine,
        prompt=prompt,
        max_tokens=40,
        n=1,
        stop=None,
        temperature=0.5,
        model=model_engine
    )
    title = res.choices[0].text.strip()
    return title

# full description
def generate_full_product_title(comment, description):
    comment = convertInitials(comment)
    prompt = (
        f"Additional Condition: {comment}."
        f"Item information: {description}."
        f"Please generate a product title in the format [Additional Condition] - [Item information], The character limit for Item information is 150 byte."
    )
    res = client.chat.completions.create(
        model=model_engine,
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.4,
    )
    print(res)
    Newdescription = res.choices[0].text.strip()
    return Newdescription

def special_characters_convert_d(description):
        try:
            if description[0] == '"' and description[-1] == '"':
                description = description.strip()
                description = description[1:-1]
        except Exception as e:
            print(e)
        description = description.replace("°"," Degree ")
        description = description.replace("™","")
        description = description.replace("®","")
        description = description.replace("©","")
        description = description.replace("w/ ","With ")
        description = description.replace("w/","With ")
        description = description.replace("W/ ","With ")
        description = description.replace("W/","With ")
        description = description.replace("，",",")
        description = description.replace("“",'"')
        description = description.replace("”",'"')
        description = description.replace("’’",'"')
        description = description.replace("’","'")
        description = description.replace("‘","'")
        description = description.replace("″",'"')
        description = description.replace("【","[")
        description = description.replace("】","]")
        description = description.replace("×","x")
        description = description.replace("–","-")
        description = description.replace("℉"," Fahrenheit scale ")
        description = description.replace(" "," ")
        description = description.replace("Φ"," ")
        description = description.replace("’","'")
        description = description.replace('Additional Condition" - "',"")
        description = description.replace("Additional Condition - ","")
        description = description.replace("Additional Condition: ","")
        description = description.replace("[Additional Condition] - ","")
        description = description.replace("Item Info: ","")
        description = description.replace("é","e")
        description = description.replace("（","(")
        description = description.replace("）",")")
        description = description.replace("≤"," less than or equal than ")
        description = description.replace("ӧ","o")
        description = description.replace("ö","o")
        description = description.replace("î","i")
        description = description.replace('"Additional Condition" - ',"")
        description = description.replace("150 Byte: ","")
        description = description.replace("150 byte: ","")
        description = description.replace("150 Byte - ","")
        description = description.replace("150 byte - ","")
        description = description.replace("[Additional Condition] ","")
        description = description.replace("ñ","n")
        description = description.replace("New - ","")
        description = description.replace("[Item information]","")
        description = description.replace("Item information: ","")
        description = description.replace("²","^2")
        description = description.replace("³","^3")
        description = description.replace("à","a")
        return description

def special_characters_convert_l(lead):
    try:
        if lead[0] == '"' and lead[-1] == '"':
            lead = lead.strip()
            lead = lead[1:-1]
        if "(" in lead:
            index1 = lead.find("(")
            index2 = lead.find(")")
            leadH = lead[:index1]
            leadB = lead[index2+1:]
            lead = leadH + leadB
        if "," in lead:
            index3 = lead.find(",")
            lead = lead[:index3]
    except Exception as e:
            print(e)
    lead = lead.replace("°","Degree")
    lead = lead.replace("™","")
    lead = lead.replace("®","")
    lead = lead.replace("©","")
    lead = lead.replace("w/ ","With ")
    lead = lead.replace("w/","With ")
    lead = lead.replace("，",",")
    lead = lead.replace("“",'"')
    lead = lead.replace("”",'"')
    lead = lead.replace("″",'"')
    lead = lead.replace("’’",'"')
    lead = lead.replace("’","'")
    lead = lead.replace("‘","'")
    lead = lead.replace("【","[")
    lead = lead.replace("】","]")
    lead = lead.replace("×","x")
    lead = lead.replace("–","-")
    lead = lead.replace("℉"," Fahrenheit scale")
    lead = lead.replace(" "," ")
    lead = lead.replace("Φ"," ")
    lead = lead.replace("î","i")
    lead = lead.replace("é","e")
    lead = lead.replace("（","(")
    lead = lead.replace("）",")")
    lead = lead.replace("≤"," less than or equal than ")
    lead = lead.replace("ӧ","o")
    lead = lead.replace("ö","o")
    lead = lead.replace("ñ","n")
    lead = lead.replace("²"," Squared")
    lead = lead.replace("à","a")
    return lead
