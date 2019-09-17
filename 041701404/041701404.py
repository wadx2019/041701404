import os
import json
import jsonpath
import re
direct_city={"北京","天津","上海","重庆"}
region_dict={"内蒙古":"内蒙古自治区","广西":"广西壮族自治区","宁夏":"宁夏回族自治区","新疆":"新疆维吾尔自治区","西藏":"西藏自治区"}

def GetPhoneNumber(raw):
    match = re.search(r"[0-9]{11}", raw)
    if match:
        return match.group(0)
    return "ErrorPhoneNumber"

def DelePhoneNumber(raw):
    return re.sub(r"[0-9]{11}","",raw)
set_Lv3_sub={"市","区","县"}
set_Lv4_sub={"街道","镇","乡"}
ret=[]
def GetLv7(now_addr):#detail
    ret[7]=now_addr

def GetLv6(now_addr):#Num
    # try:
        #print("Lv6" + now_addr)
        match = re.match(r"(.*[0-9]+号?)", now_addr)
        if match:
            #print("666"+match.group(0))
            ret[6] = match.group(0)
            now_addr = re.sub(r".*[0-9]+号?", "", now_addr)
        GetLv7(now_addr)
    # except:
    #     return

def GetLv5(now_addr):#street
    try:
        #print("Lv5" + now_addr)
        if(level==1):
            ret[5] = now_addr
            return
        else:
            match=re.match(r".*(路|街|巷|弄)",now_addr)
            if match:
                ret[5]=match.group(0)
                now_addr=re.sub(r".*(路|街|巷|弄)","",now_addr)
            GetLv6(now_addr)
    except:
        return

def GetLv4(now_addr,now_dict):#street
    try:
        #print("Lv4" + now_addr)
        if len(now_dict) == 1:
            for i in now_dict:
                #print(now_dict[i])
                now_dict = now_dict[i]['c']
                break
            GetLv5(now_addr, now_dict)
            return
        for street_dict in now_dict:
            now_path = now_dict[street_dict]
            try_street = now_path['n']
            p = -1
            while p < len(now_addr):
                p = p + 1
                # #print(addr[lst:p])
                if (now_addr[0:p].find(try_street) >= 0):
                    street = try_street
                    #print("!!!" + now_addr[p:p + 2])
                    if now_addr[p] in set_Lv4_sub:
                        street = street + now_addr[p]
                        p += 1
                    if now_addr[p:p + 2] in set_Lv4_sub:
                        street = street + now_addr[p:p + 2]
                        p += 2
                    #print(street)
                    ret[4] = street
                    GetLv5(now_addr[p:])
                    return
        GetLv5(now_addr)
        return
    except:
        return

def GetLv3(now_addr,now_dict):#country
    try:
        #print("Lv3" + now_addr)
        if len(now_dict) == 1:
            for i in now_dict:
                # #print(now_dict[i])
                now_dict = now_dict[i]['c']
                break
            GetLv4(now_addr, now_dict)
            return

        for country_dict in now_dict:
            now_path = now_dict[country_dict]
            try_country = now_path['n']
            p = -1
            while p < len(now_addr):
                p = p + 1
                # #print(addr[lst:p])
                if (now_addr[0:p].find(try_country) >= 0):
                    country = try_country

                    # #print("!!!"+now_addr[p])
                    if now_addr[p] in set_Lv3_sub:
                        country = country + now_addr[p]
                        p += 1
                    #print(country)
                    ret[3] = country
                    GetLv4(now_addr[p:], now_path['c'])
                    return
        GetLv4(now_addr, now_dict)
        return
    except:
        return

def GetLv2(now_addr,now_dict):#city
    try:
        if len(now_dict) == 1:
            for i in now_dict:
                #print(now_dict[i])
                now_dict = now_dict[i]['c']
                break
            GetLv3(now_addr, now_dict)
            return
        #print("Lv2" + now_addr)
        for city_dict in now_dict:
            now_path = now_dict[city_dict]
            try_city = now_path['n']
            p = -1
            while p < len(now_addr):
                p = p + 1
                if (now_addr[0:p].find(try_city) >= 0):
                    city = try_city
                    city = city + "市"
                    ret[2] = (city)
                    #print(city)
                    GetLv3(now_addr[p:], now_path['c'])
                    return

        GetLv3(now_addr, now_dict)
        return
    except:
        return

def GetLv1(now_addr,now_dict):#province
    try:
        #print("Lv1" + now_addr)
        if len(now_dict) == 1:
            for i in now_dict:
                #print(now_dict[i])
                now_dict = now_dict[i]['c']
                break
            GetLv1(now_addr, now_dict)
            return

        for prov_dict in now_dict:
            now_path = now_dict[prov_dict]
            try_pronvince = now_path['n']
            # #print(try_pronvince)

            p = -1
            while p < len(now_addr):
                p = p + 1
                # #print(addr[lst:p])
                if (now_addr[0:p].find(try_pronvince) >= 0):
                    province = try_pronvince

                    if province not in direct_city:  # 不是直辖市
                        flag = False
                        for s_name, f_name in region_dict.items():
                            # #print(s_name + "," + f_name)
                            if (province == s_name):
                                province = f_name
                                flag = True
                                break
                        if flag == False:
                            province += "省"

                        ret[1] = (province)
                        #print(province)
                        GetLv2(now_addr[p:], now_path['c'])
                    else:
                        ret[1] = (province)
                        ret[2] = (province + "市")  # 市=直辖市
                        #print(province)
                        GetLv2(now_addr[p:], now_path['c'])

                        # ret[1]=(province)#省=直辖
                        # ret[2]=(province+"市")#市=直辖市
                        # #print(province+"市")
                        # GetLv3(now_addr[p:], now_path['c'])

                    return
        GetLv2(now_addr, now_dict)
        return
    except:
        return

def Split5(raw):
    try:
        PhoneNumber = GetPhoneNumber(raw)
        raw = DelePhoneNumber(raw)  # dele phone
        ret = []
        #print(raw)
        GetLv1(raw, json_list)
        return PhoneNumber
    except:
        return "error"

if __name__ == '__main__':
    json_file = open(r'db.json', 'rb')
    data = json_file.read()
    json_list = json.loads(data)
    input_info =input()
    info_list = input_info.split()
    output_list = []

    for info in info_list:
        try:
            ret.clear()
            for i in range(10):
                ret.append("")
            level = int(info[0])
            tmp = info[2:]
            name = tmp.split(",")[0]
            addr = tmp.split(",")[1]
            addr = addr.replace(".", "")
            #print(name + "," + addr)
            PhoneNumber = Split5(addr)
            #print(ret)
            tmp_address_list = []
            tmp_address_list.clear()
            if level == 1:
                for i in range(5):
                    tmp_address_list.append(ret[i + 1])
            else:
                for i in range(7):
                    tmp_address_list.append(ret[i + 1])
            tmp_output_info = {}
            tmp_output_info.clear()
            tmp_output_info["姓名"] = name
            tmp_output_info["手机"] = PhoneNumber
            tmp_output_info["地址"] = tmp_address_list
            output_list.append(tmp_output_info)
        except:
            continue
    try:
        output_json = json.dumps(output_list, indent=4)
        output_json = output_json.encode('utf-8').decode('unicode_escape')
        print(output_json)
        # output_file = open("2.txt", "w")
        # output_file.write(output_json)
    except:
        pass


