import MeCab
import CaboCha
import re
import sqlite3
import CaboCha


class Analysis:

    con = None

    def __init__(self, db = True):
        self.cabocha = CaboCha.Parser()
        self.mecab = MeCab.Tagger ("-Ochasen")
        self.sentences = []
        self.sentence = []
        self.syntax = []
        self.con = sqlite3.connect("iori.db", isolation_level=None)

        self.use_db = db

    def analysis(self, txt):
        self.lexer(txt)
        self.split_sentence()
        for s in self.sentences:
            if s == []:
                continue
            self.parser(s)
        res = self.Cabocha(txt)
        #for r in res:
        #    print(r[0]+" -> "+r[1])
        print("#"*5)


    def finish(self):
         self.con.close()

    def split_sentence(self):
        self.sentences = []
        tmp = []
        for w in self.sentence:
            if "句点" in w[2]:
                self.sentences.append(tmp)
                tmp = []
            else:
                tmp.append(w)
        self.sentences.append(tmp)
        #print(self.sentences)


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

        """
        print(AdvPs)
        print(PreNs)
        print(NPs)
        print(As)
        print(Vs)
        print(Cs)
        """

        while self.syntax.count("") > 0:
            self.syntax.remove("")

        """
        for w in self.syntax:
            print(w[0], end=" ")
        print("")

        for w in self.syntax:
            print(w[1], end=" ")
        print("")
        """

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
        CMP= ""
        pos = 0
        for w in context:
            if re.match(r"^動詞",w[2]) != None:
                V = w[0]
                self.insert_db("V", V)

            elif re.match(r"(接続)?助動?詞", w[2]) != None:
                if V != "":
                    CMP = w[0]
                    self.insert_db("CMP", CMP)
                    self.vplink(V, CMP)

                    Vs.append( ( V+CMP, "VP"))
                    self.syntax[pos] = "CMP", V
                    V = ""
                    CMP = ""

            pos += 1

        if V != "":
            Vs.append( ( V, "V"))
            self.syntax[pos] = "V", V

            self.insert_db("V", V)

        return Vs

    def A(self, context):
        As = []
        A = ""
        CMP= ""
        pos = 0
        for w in context:
            if re.match(r".*形容動*詞", w[2]) != None:
                A = w[0]
                self.insert_db("A", A)

            elif "助動詞" in w[2]:
                if A != "":
                    CMP = w[0]
                    self.insert_db("CMP", CMP)
                    self.aplink(A, CMP)

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
        if re.match(r"^名詞.*[^(形容動詞語幹)]$", w1[2]) != None and \
            re.match(r"助動?詞", w2[2]) != None:

            self.insert_db("N", w1[0])
            self.insert_db("CMP", w2[0])
            self.nplink(w1[0], w2[0])

            return w1[0]+w2[0], "NP"

        elif re.match(r"^名詞.*[^(形容動詞語幹)]$", w1[2]) != None:

            self.insert_db("N", w1[0])

            return w1[0], "N"
        return None

    def Word(self, tree, chunk):
        word = ''
        cmp  = ""
        TYPE = ""
        for i in range(chunk.token_pos, chunk.token_pos + chunk.token_size):
            token = tree.token(i)
            features = token.feature.split(',')

            #print(features[0]+":"+token.surface)

            if features[0] == '名詞':
                word += token.surface
                TYPE = features[0] 
            elif features[0] == '形容詞':
                word += token.surface
                TYPE = features[0]                 
            elif features[0] == '動詞':
                word += token.surface
                TYPE = features[0]
            elif features[0] == '副詞':
                word += token.surface #features[6]
                TYPE = features[0]

            elif features[0] == '記号':
                word += token.surface
                TYPE = features[0]
                break
            elif features[0] == '接続詞':
                word += token.surface #features[6]
                TYPE = features[0]
                break


            elif re.match(r"助動?詞", features[0]) != None:
                cmp = features[6]
                break

            else:
                break

        return word, cmp, TYPE

    def Cabocha(self, sentence):
        tree = self.cabocha.parse(sentence)
        chunk_dic = {}
        chunk_id = 0
        for i in range(0, tree.size()):
            token = tree.token(i)
            if token.chunk:
                chunk_dic[chunk_id] = token.chunk
                chunk_id += 1

        pairs = []
        for chunk_id, chunk in chunk_dic.items():
            if chunk.link > 0:
                from_word, fcmp, ftype =  self.Word(tree, chunk)

                #if fcmp:
                #    from_word += "<" + fcmp + ">"

                to_chunk = chunk_dic[chunk.link]
                to_word, tcmp, ttype = self.Word(tree, to_chunk)

                #if tcmp:
                #   to_word += "<" + tcmp + ">"

                self.slink(from_word, ftype, to_word, ttype)

                #print(from_word+" "+to_word)
                pairs.append((from_word, to_word))

        return pairs

    def vplink(self, v, cmp):
        print("vplink "+ v +"<-->"+ cmp)
        if not self.use_db:
            return

        iquery = "insert into VPLINK values( null, ?, ?, ?);"

        src = self.con.execute("select * from V where word='"+v+"';").fetchone()[0]
        dst = self.con.execute("select * from CMP where word='"+cmp+"';").fetchone()[0]

        c = self.con.execute("select  * from VPLINK where src='"+str(src)+"' and dst='"+str(dst)+"';")
        res = c.fetchone()
        if res is None:
            self.con.execute( iquery, ( src, dst, 1))
        else:
            count = int(res[3]) + 1
            self.con.execute( "update VPLINK set wei="+ str(count) +" where src='" +str(src)+ "' and dst='"+str(dst)+"';")

    def aplink(self, a, cmp):

        print("aplink "+ a +"<-->"+ cmp)
        if not self.use_db:
            return

        iquery = "insert into APLINK values( null, ?, ?, ?);"

        src = self.con.execute("select * from A where word='"+a+"';").fetchone()[0]
        dst = self.con.execute("select * from CMP where word='"+cmp+"';").fetchone()[0]

        c = self.con.execute("select  * from APLINK where src='"+str(src)+"' and dst='"+str(dst)+"';")
        res = c.fetchone()
        if res is None:
            self.con.execute( iquery, ( src, dst, 1))
        else:
            count = int(res[3]) + 1
            self.con.execute( "update APLINK set wei="+ str(count) +" where src='" +str(src)+ "' and dst='"+str(dst)+"';")

    def nplink(self, n, cmp):

        print("nplink "+ n +"<-->"+ cmp)
        if not self.use_db:
            return

        iquery = "insert into NPLINK values( null, ?, ?, ?);"

        src = self.con.execute("select * from N where word='"+n+"';").fetchone()[0]
        dst = self.con.execute("select * from CMP where word='"+cmp+"';").fetchone()[0]

        c = self.con.execute("select  * from NPLINK where src='"+str(src)+"' and dst='"+str(dst)+"';")
        res = c.fetchone()
        if res is None:
            self.con.execute( iquery, ( src, dst, 1))
        else:
            count = int(res[3]) + 1
            self.con.execute( "update NPLINK set wei="+ str(count) +" where src='" +str(src)+ "' and dst='"+str(dst)+"';")

    def slink(self, s, st, d, dt):

        print("slink "+ s +"["+ st +"]<-->"+ d +"["+ dt +"]")
        exist = True

        if not self.use_db:
            return

        if not st or not dt or not s or not d:
            return

        tables= {
            "名詞":"NP",
            "動詞":"VP",
            "形容詞":"AP",
            "副詞":"Adv",
            "接続詞":"C",
            "記号":"S"
        } 

        iquery = "insert into LINK values( null, ?, ?, ?);"

        sdat = self.con.execute("select * from "+tables[st]+" where word='"+s+"';").fetchone()
        ddat = self.con.execute("select * from "+tables[dt]+" where word='"+d+"';").fetchone()

        if sdat:
            src = sdat[0]
        else:
            self.insert_db(tables[st], s)
            exist = False

        if ddat:
            dst = ddat[0]
        else:
            self.insert_db(tables[dt], d)
            exist = False

        if exist:
            c = self.con.execute("select  * from LINK where src='"+str(src)+"' and dst='"+str(dst)+"';")
            res = c.fetchone()
            if res is None:
                self.con.execute( iquery, ( src, dst, 1))
            else:
                count = int(res[3]) + 1
                self.con.execute( "update LINK set wei="+ str(count) +" where src='" +str(src)+ "' and dst='"+str(dst)+"';")

    def insert_db(self, table, word):
        #print("insert "+word+" to "+ table)
        if not self.use_db:
            return

        iquery = "insert into "+table+" values( null, ?, ?);"
        c = self.con.execute("select  * from "+ table +" where word='"+word+"';")
        res = c.fetchone()
        if res is None:
            self.con.execute( iquery, ( word, 1))
        else:
            count = int(res[2]) + 1
            self.con.execute( "update "+table+" set count="+ str(count) +" where word='" +word+ "';")

    def create_db(self):
        if not self.use_db:
            return

        table_name = ["N", "CMP", "V", "A", "C", "Adv", "PreN", "NP", "VP", "AP", "S"]
        for name in table_name:
            c = """
            create table """+ name +"""(
                id integer primary key autoincrement,
                word text,
                count integer
            );
            """
            self.con.execute(c)
        link_table_name = ["NPLINK", "VPLINK", "APLINK", "LINK"]
        for name in link_table_name:
            self.con.execute("""            
                create table """+ name +"""(
                    id integer primary key autoincrement,
                    src integer,
                    dst integer,
                    wei integer
                );""")

    def drop_db(self):
        if not self.use_db:
            return

        table_name = ["N", "CMP", "V", "A", "C", "Adv", "PreN", "NPLINK", "VPLINK", "APLINK", "LINK"]
        for name in table_name:
            c = "drop table "+ name +";"
            self.con.execute(c)
        self.con.execute("drop table LINK;")


class Generate:

    con = None

    def __init__(self):
        self.cabocha = CaboCha.Parser()
        self.mecab = MeCab.Tagger ("-Ochasen")
        self.sentences = []
        self.sentence = []
        self.con = sqlite3.connect("iori.db", isolation_level=None)

    def finish(self):
         self.con.close()

    def random(self, n):
        #TODO
        return 1

    def say(self):
        what = random(5)

    def N(self):

        c = self.con.execute("select max(id) from N;")
        res = c.fetchone()
        if res is None:
            raise RuntimeError("DB not found!!")
        else:
            print(res)


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

