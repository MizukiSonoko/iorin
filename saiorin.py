import sqlite3
import random


class Generate:

    con = None

    def __init__(self):
        self.sentences = []
        self.sentence = []
        self.con = sqlite3.connect("iori.db", isolation_level=None)

    def finish(self):
         self.con.close()

    def random(self, n):
        return random.randint(1, n-1)


    def say(self):
        sentence = self.Sentence()
        think = self.random(4)
        if think == 0:
            print(sentence + "！")
        elif think == 1:
            print(sentence + "〜")
        else:
            print(sentence)

    def Sentence(self):
        sentence = ""
        cnt = 0
        while True:
            think = self.random(4)
            if think == 0:
                AP = self.AP()
                sentence += AP

                cnt += 1

            elif think == 1:
                NP = self.VP()
                sentence += NP

                cnt += 1

            elif think == 2:
                Adv = self.Adv()
                sentence += Adv

                cnt += 1

            elif think == 3:
                VP = self.VP()
                sentence += VP

                if cnt > 3:
                    break
            else:
                if cnt > 3:
                    break
        return sentence



    def AP(self):
        Aid, A = self.A() 
        phrase =  self.__get_phrase(Aid, A, "APLINK")
        if not phrase:
            return A
        return phrase

    def VP(self):
        Vid, V = self.V() 
        phrase =  self.__get_phrase(Vid, V, "VPLINK")
        if not phrase:
            return V
        return phrase

    def NP(self):
        Nid, N = self.N() 
        phrase =  self.__get_phrase(Nid, N, "NPLINK")
        if not phrase:
            return N
        return phrase
        
    def Adv(self):
        return str(self.__get_word("Adv")[1])


    def A(self):
        return self.__get_word("A")

    def V(self):
        return self.__get_word("V")

    def N(self):
        return self.__get_word("N")


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
    g.say()
    g.finish()

