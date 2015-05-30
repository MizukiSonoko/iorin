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
        print(sentence)


    def AP(self):
        Aid, A= self.A() 
        c = self.con.execute("select src, dst from APLINK where src="+ str(Aid) +";")
        res = c.fetchone()
        if res is None:
            return "ね"
            #raise RuntimeError("Link data not found!!")
        cmpid = res[1]
        c = self.con.execute("select word from CMP where id="+ str(cmpid) +";")
        res = c.fetchone()
        if res is None:
            raise RuntimeError("CMP data not found!!")

        return A + res[0]

    def VP(self):
        Vid, V = self.V() 
        c = self.con.execute("select src, dst from VPLINK where src="+ str(Vid) +";")
        res = c.fetchone()
        if res is None:
            return V
            #raise RuntimeError("Link data not found!!")

        cmpid = res[1]
        c = self.con.execute("select word from CMP where id="+ str(cmpid) +";")
        res = c.fetchone()
        if res is None:
            return V + "だ"
            #raise RuntimeError("CMP data not found!!")

        return V + res[0]
        

    def NP(self):
        Nid, N = self.N() 
        c = self.con.execute("select src, dst from NPLINK where src="+ str(Nid) +";")
        res = c.fetchone()
        if res is None:
            return N
            #raise RuntimeError("Link data not found!!")

        cmpid = res[1]
        c = self.con.execute("select word from CMP where id="+ str(cmpid) +";")
        res = c.fetchone()
        if res is None:
            return N + "が"
            #raise RuntimeError("CMP data not found!!")

        return N + res[0]
        
    def Sentence(self):
        NP = self.NP()
        think = self.random(3)
        if think == 0:
            AP = self.AP()
            return NP + AP
        else:
            VP = self.VP()
            return NP + VP


    def A(self):
        c = self.con.execute("select max(id) from A;")
        res = c.fetchone()
        if res is None:
            raise RuntimeError("DB not found!!")
        id = self.random(res[0])
        c = self.con.execute("select id, word from A where id="+ str(id) + ";")
        res = c.fetchone()
        if res is None:
            raise RuntimeError("Data dose not exist!")

        return res[0], res[1]


    def V(self):
        c = self.con.execute("select max(id) from V;")
        res = c.fetchone()
        if res is None:
            raise RuntimeError("DB not found!!")
        id = self.random(res[0])
        c = self.con.execute("select id, word from V where id="+ str(id) + ";")
        res = c.fetchone()
        if res is None:
            raise RuntimeError("Data dose not exist!")

        return res[0], res[1]


    def N(self):
        c = self.con.execute("select max(id) from N;")
        res = c.fetchone()
        if res is None:
            raise RuntimeError("DB not found!!")
        id = self.random(res[0])
        c = self.con.execute("select id, word from N where id="+ str(id) + ";")
        res = c.fetchone()
        if res is None:
            raise RuntimeError("Data dose not exist!")

        return res[0], res[1]

if __name__ == "__main__":


    g = Generate()
    g.say()
    g.finish()
