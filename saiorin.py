import sqlite3
import random


class Generate:

    con = None

    def __init__(self, db=None):
        self.sentences = []
        self.sentence = []
        if db:
            self.con = sqlite3.connect(db, isolation_level=None)
        else:
            self.con = sqlite3.connect("iori.db", isolation_level=None)

    def finish(self):
         self.con.close()

    def random(self, n):
        return random.randint(1, n-1)


    def say(self):
        sentence = self.Sentence()
        return sentence

    def rule(self, typ):
        #print("type:"+typ)
        if typ == "Adv":
            return [self.VP, self.NP, self.AP]
        elif typ == "VP":
            return [self.C, self.END]
        elif typ == "AP":
            return [self.C, self.NP, self.END]
        elif typ == "C" or typ == "BEGIN":
            return [self.VP, self.AP, self.NP]
        elif typ == "NP":
            return [self.NP, self.AP]
        elif typ == "N" or typ == "A" or typ == "V":
            return [self.CMP]
        elif typ == "CMP":
            return [self.NP, self.VP, self.AP]
        else:
            #print(typ)
            return [self.END]

    def Sentence(self):
        syntax = ["BEGIN"]

        sentence = ""
        cnt = 0
        
        while True:
            Rs = self.rule(syntax[-1])
            if len(Rs) == 1:
                think = 0
            else:
                think = self.random(len(Rs))
            
            phrase, typ = Rs[think]()
#            print("P:"+str(phrase) + "type:"+ str(typ))
            syntax.append(typ)
            sentence += phrase
            if typ == "END":
                break
  
        print(syntax)
        return sentence



    def AP(self):
        Aid, A = self.A() 
        phrase =  self.__get_phrase(Aid, A, "APLINK")
        if not phrase:
            return A, "A"
        return phrase, "AP"

    def VP(self):
        Vid, V = self.V() 
        phrase =  self.__get_phrase(Vid, V, "VPLINK")
        if not phrase:
            return V, "V"
        return phrase, "VP"

    def NP(self):
        Nid, N = self.N() 
        phrase =  self.__get_phrase(Nid, N, "NPLINK")
        if not phrase:
            return N, "N"
        return phrase, "NP"
        
    def Adv(self):
        return str(self.__get_word("Adv")[1]), "Adv"

    def END(self):
        think = self.random(5)
        if think == 1:
            txt = "。"
        elif think == 2:
            txt = "！"
        elif think == 3:
            txt = "〜"
        else:
            txt = ""
        return txt, "END"

    def A(self):
        return self.__get_word("A")

    def V(self):
        return self.__get_word("V")

    def N(self):
        return self.__get_word("N")

    def C(self):
        return self.__get_word("C")[1], "C"

    def CMP(self):
        return self.__get_word("CMP")[1], "CMP"

    def __get_phrase(self, id, word, table):

        c = self.con.execute("select src, dst from "+ table +" where src="+ str(id) +";")
        res = c.fetchone()
        if res is None:
            return None
            #raise RuntimeError("Link data not found!!")

        cmpid = res[1]
        c = self.con.execute("select word from CMP where id="+ str(cmpid) +";")
        res = c.fetchone()
        if res is None:
            return None
            #raise RuntimeError("CMP data not found!!")

        return word + res[0]

    def __get_word(self, table):

        c = self.con.execute("select max(id) from " + table + ";")
        res = c.fetchone()
        if res is None:
            raise RuntimeError(V + " DB not found!!")
        id = self.random(res[0])
        c = self.con.execute("select id, word from " + table + " where id="+ str(id) + ";")
        res = c.fetchone()
        if res is None:
            raise RuntimeError("Data dose not exist!")

        return res[0], res[1]

if __name__ == "__main__":


    g = Generate()
    print(g.say())
    g.finish()

