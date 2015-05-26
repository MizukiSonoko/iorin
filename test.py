import MeCab
import re

import sqlite3

class Analysis:
   
    con = None

    def __init__(self):
        self.mecab = MeCab.Tagger ("-Ochasen")
        self.sentences = []
        self.sentence = []
        self.syntax = []
        self.con = sqlite3.connect("iori.db", isolation_level=None)        

    def analysis(self, txt):
        self.lexer(txt)
        self.split()
        for s in self.sentences:
            if s == []:
                continue
            self.parser(s)
            print("#"*5)

    def finish(self):
         self.con.close()

    def lexer(self, txt):
        self.sentence = []
        mecab = MeCab.Tagger ("-Ochasen")
        dat = mecab.parse(txt)
        lstmp1 = dat.split("\n")
        for col in lstmp1:
            lstmp = col.split("\t")
            while '' in lstmp:
                lstmp.remove('')
            if len(lstmp) > 3:
                self.sentence.append((lstmp[0], lstmp[1], lstmp[3]))
        #print(self.sentence)
    
    def split(self):
        self.sentences = []
        tmp = []
        for w in self.sentence:
            if "句点" in w[2]: 
                self.sentences.append(tmp)
                tmp = []
            else:
                tmp.append(w)
        self.sentences.append(tmp)
        print(self.sentences)

    def parser(self, sentence):
        self.syntax = [""] * ( len(sentence) + 1) 
        NPs = []
        pos = 0
        for i in range(0, len(sentence)-1):
            tmp = self.NP(sentence[i], sentence[i+1])
            if tmp != None:
                NPs.append(tmp)
                self.syntax[pos] = tmp[1], tmp[0]
            pos += 1
        Vs = self.V(sentence)
        Cs, AdvPs, PreNs= self.CAdvPreN(sentence)
        As = self.A(sentence)

        print(AdvPs)
        print(PreNs)
        print(NPs)  
        print(As)
        print(Vs)
        print(Cs)

        while self.syntax.count("") > 0:
            self.syntax.remove("")

        for w in self.syntax:
            print(w[0], end=" ")
        print("")

        for w in self.syntax:
            print(w[1], end=" ")
        print("")

    def CAdvPreN(self, context):
        Cs = []
        AdvPs = []
        PreNs = []
        pos = 0
        for w in context:
            if re.match(r"^接続詞$", w[2]) != None:
                Cs.append( (w[0], "C"))
                self.syntax[pos] = "C", w[0]

                self.insert_db("C", w[0])

            elif "副詞" in w[2]:            
                AdvPs.append( ( w[0], "AdvP" ))
                self.syntax[pos] = "AdvP", w[0]

                self.insert_db("Adv", w[0])

            elif "連体詞" in w[2]:
                PreNs.append( ( w[0], "PreN" ))
                self.syntax[pos] = "PreN", w[0]
        
                self.insert_db("PreN", w[0])

            pos += 1
        return Cs, AdvPs, PreNs
                        
    def V(self, context):
        Vs = []
        Cs = []
        V = ""
        pos = 0
        for w in context:
            if re.match(r"^動詞",w[2]) != None:
                V += w[0]

            elif re.match(r"(接続)?助動?詞", w[2]) != None:
                if V != "":
                    V += w[0]
                    Vs.append( ( V, "V"))
                    self.syntax[pos] = "V", V

                    self.insert_db("V", V)

                    V = ""
            pos += 1
        if V != "":
            Vs.append( ( V, "V"))
            self.syntax[pos] = "V", V

            self.insert_db("V", V)

        return Vs

    def A(self, context):
        As = []
        A = ""
        pos = 0
        for w in context:
            if re.match(r".*形容動*詞", w[2]) != None:
                A += w[0]

            elif "助動詞" in w[2]:
                if A != "":
                    A += w[0]
                    As.append( (A, "A"))
                    self.syntax[pos] = "A", A
                    
                    self.insert_db("A", A)

                    A = ""
            pos += 1
        if A != "":
            As.append( ( A, "A"))
            self.sytnax[pos] = "A", A
            self.insert_db("A", A)

        return As        
                        
    def NP(self, w1, w2):
        if len(w1) < 3 or len(w2) < 3:
            return None
        if re.match(r"^名詞.*[^(形容動詞語幹)]$", w1[2]) != None and re.match(r"助動?詞", w2[2]) != None:
            
            self.insert_db("N", w1[0])
            self.insert_db("CMP", w2[0])
            
            self.link(w1[0],"N" , w2[0],"CMP")

            if "ガ" in w2[1]:
                return w1[0] + w2[0], "NPga"
            elif "ニ" in w2[1]:
                return w1[0] + w2[0], "NPni"
            elif "ヲ" in w2[1]:
                return w1[0] + w2[0], "NPo"
            elif "ノ" in w2[1]:
                return w1[0] + w2[0], "NPno"
            elif "ヘ" in w2[1]:
                return w1[0] + w2[0], "NPe"
            elif "カラ" in w2[1]:
                return w1[0] + w2[0], "NPkara"
            elif "モ" in w2[1]:
                return w1[0] + w2[0], "NPmo"
            elif "デ" in w2[1]:
                return w1[0] + w2[0], "NPde"
            elif "ナ" in w2[1]:
                return w1[0] + w2[0], "NPna"
            return w1[0] + w2[0], "NPundef"
        elif re.match(r"^名詞.*[^(形容動詞語幹)]$", w1[2]) != None:

            self.insert_db("N", w1[0])

            return w1[0], "N"
        return None


    def link(self, s, st, d, dt):
        iquery = "insert into LINK values( null, ?, ?, ?);"
    
        src = self.con.execute("select * from "+ st + " where word='"+s+"';").fetchone()[0]
        dst = self.con.execute("select * from "+ dt + " where word='"+d+"';").fetchone()[0]

        c = self.con.execute("select  * from LINK where src='"+str(src)+"' and dst='"+str(dst)+"';")
        res = c.fetchone()
        if res is None:
            self.con.execute( iquery, ( src, dst, 1))
        else:
            count = int(res[3]) + 1
            self.con.execute( "update LINK set wei="+ str(count) +" where src='" +str(src)+ "' and dst='"+str(dst)+"';")
        
    def insert_db(self, table, word):
        iquery = "insert into "+table+" values( null, ?, ?);"
        c = self.con.execute("select  * from "+ table +" where word='"+word+"';")
        res = c.fetchone()
        if res is None:
            self.con.execute( iquery, ( word, 1))
        else:
            count = int(res[2]) + 1
            self.con.execute( "update "+table+" set count="+ str(count) +" where word='" +word+ "';")
         
    def create_db(self):
        table_name = ["N", "CMP", "V", "A", "C", "Adv", "PreN"]
        for name in table_name:
            c = """
            create table """+ name +"""(
                id integer primary key autoincrement,
                word text,
                count integer
            );
            """
            self.con.execute(c)
        self.con.execute("""
            create table LINK(
                id integer primary key autoincrement,
                src integer,
                dst integer,
                wei integer
            );""")
        
    def drop_db(self): 
        table_name = ["N", "CMP", "V", "A", "C", "Adv", "PreN"]
        for name in table_name:
            c = "drop table "+ name +";"
            self.con.execute(c)
        self.con.execute("drop table LINK;")

if __name__ == "__main__":
    a = Analysis()
    #a.drop_db()
    a.create_db()
    
    print("="*20)
    s = "つい最近ミズキが転んで泣いた。そして、ゆっくり立ち上がった。"
    print(s)
    a.analysis(s)
    print("="*20)
    s = "千夜ちゃん、この前の英語のノート見せてくれる？"
    print(s)
    a.analysis(s)
    print("="*20)
    s = "私もシャロさんみたいな姉が欲しかったです。"
    print(s)
    a.analysis(s)
    print("="*20)
    s = "私、夕日の中で何度も倒れながら特訓するのがあこがれで～"
    print(s)
    a.analysis(s)
    print("="*20)
    s = "だんだんココアっぽくなってきてないか……？"
    print(s)
    a.analysis(s)
    print("="*20)
    
    
    #a.analysis("ミズキが踊る")
    #print("="*20+"\nV[ga,o]\n")
    #a.analysis("ミズキがイオリを食べた")
    #a.analysis("ミズキがイオリを食べる")
    #a.analysis("ミズキがイオリを読んだ")
    #a.analysis("ミズキがイオリを呼ぶ")
    #print("="*20+"\nV[ni,ga]\n")
    #a.analysis("ミズキにイオリが届いた")
    #a.analysis("ミズキにイオリが届く")
    #a.analysis("ミズキにイオリが現れた")
    #a.analysis("ミズキにイオリが被さった")
    print("="*20)
    a.analysis("ミズキをイオリが食べた、そして結婚した。")
    print("="*20)
    a.finish()

"""
ミズキ  ミズキ  ミズキ  名詞-一般
が  ガ  が  助詞-格助詞-一般
リンゴ  リンゴ  リンゴ  名詞-一般
を  ヲ  を  助詞-格助詞-一般
食べる  タベル  食べる  動詞-自立   一段    基本形
"""
