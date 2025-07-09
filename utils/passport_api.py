import requests
from urllib.parse import quote

# Common headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://passport.ics.gov.et",
    "Referer": "https://passport.ics.gov.et/",
    "Content-Type": "application/json",
}

def check_by_reference(reference, lang="en"):
    try:

        ref_value = reference.strip()
        json_data = {"Tracking_Code": ref_value}
        if len(ref_value) < 7:
            return "❌ Tracking Code must be at least 7 characters long \."
        res = requests.post(
            "https://passport.ics.gov.et/track",
            json=json_data,
            headers=HEADERS,
            timeout=10
        )
        data = res.json()
        # print("Response from /track:", data)

        if not isinstance(data, list) or len(data) == 0:
            return ("❌ Your passport is either not ready or the input is invalid \. \n"
                    "⏱ ይቅርታ ፓስፖርትዎ አልደረሰም\! እባክዎን በትዕግስት ይጠብቁ\!")

        messages = []
        for d in data:
            messages.append(
                f"✅ **እንኳን ደስ አለዎት\!**\n\n"
            f"ፓስፖርትዎ ስለደረስ **{d['brancham']}** ለእርስዎ በተፈቀደልዎ መቀበያ ቀናት ብቻ በመቅረብ መውሰድ ይችላሉ\!\n\n"
            
            f"📄 **Tracking Code:**\n``` {d['ref_code']}```\n"
            f"👤 **ሙሉ ስም / Full Name:**\n``` {d['name']} {d['fathers_name']} {d['grand_fathers_name']}```\n"
            f"📍 **መቀበያ ቦታ / Pickup Location:**\n``` {d['branch']} ({d['brancham']})```\n"
            f"📅 **መቀበያ ቀን / Receiving Date:**\n``` {d['date']} ({d['dateam'].strip()})```"

            )
        return "\n\n".join(messages)

    except Exception as e:
        print(f"Error in check_by_reference: {e}")
        return ("❌ Your passport is either not ready or the input is invalid \. \n"
                "⏱ ይቅርታ ፓስፖርትዎ አልደረሰም\! እባክዎን በትዕግስት ይጠብቁ\!")


def check_by_fullname(full_name, branch, lang="en"):
    try:
        if len(full_name.split(" ")) < 3:
            return "❌ Please enter your full name including your Grandfather's Name \."
        encoded_name = quote(full_name)
        encoded_branch = quote(branch)

        url = f"https://passport.ics.gov.et/info?fullName={encoded_name}&branch={encoded_branch}"
        res = requests.get(url, headers=HEADERS, timeout=10)
        # print("Response from /info:", res)
        json_resp = res.json()

        if not json_resp.get("ok"):
            return ("❌ Your passport is either not ready or the input is invalid \. \n"
                    "⏱ ይቅርታ ፓስፖርትዎ አልደረሰም\! እባክዎን በትዕግስት ይጠብቁ\!")

        d = json_resp["data"]
        return (
            f"✅ **እንኳን ደስ አለዎት\!**\n\n"
            f"ፓስፖርትዎ ስለደረስ **{d['brancham']}** ለእርስዎ በተፈቀደልዎ መቀበያ ቀናት ብቻ በመቅረብ መውሰድ ይችላሉ\!\n\n"
            
            f"📄 **Tracking Code:**\n``` {d['ref_code']}```\n"
            f"👤 **ሙሉ ስም / Full Name:**\n``` {d['name']} {d['fathers_name']} {d['grand_fathers_name']}```\n"
            f"📍 **መቀበያ ቦታ / Pickup Location:**\n``` {d['branch']} ({d['brancham']})```\n"
            f"📅 **መቀበያ ቀን / Receiving Date:**\n``` {d['date']} ({d['dateam'].strip()})```"

        )
    except Exception as e:
        print(f"Error in check_by_fullname: {e}")
        return ("❌ Your passport is either not ready or the input is invalid \. \n"
                "⏱ ይቅርታ ፓስፖርትዎ አልደረሰም\! እባክዎን በትዕግስት ይጠብቁ\!")


# print(check_by_fullname("ABEBE KEBEDE HAILE", "ICS Saris Adey Abeba Branch", "en"))
# print(check_by_reference("AAL1234567", "en"))