import MeCab

class Analysis:
    
    def __init__(self):
        self.mecab = MeCab.Tagger ("-Ochasen")
        self.sentences = []
        self.sentence = []
        self.syntax = []
    
    def analysis(self, txt):
        self.lexer(txt)
        self.split()
        for s in self.sentences:
            if s == []:
                continue
            self.parser(s)
            print("#"*5)

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
        self.syntax = []
        NPs = []
        for i in range(0, len(sentence)-1):
            tmp = self.NP(sentence[i], sentence[i+1])
            if tmp != None:
                NPs.append(tmp)
        Vs = self.V(sentence)
        AdvP = self.AdvP(sentence)
        As = self.A(sentence)
        print(AdvP)
        print(NPs)  
        print(As)
        print(Vs)
               
    def V(self, context):
        Vs = []
        V = ""
        for w in context:
            if "動詞" in w[2] and not "助" in w[2] and not "名" in w[2]:
                V += w[0]
            elif "接続助詞" in w[2]:
                if V != "":
                    V += w[0]
                    Vs.append( ( V, "Vc"))
                    V = ""
        if V != "":
            Vs.append( ( V, "V"))
        return Vs

    def A(self, context):
        As = []
        A = ""
        for w in context:
            if "形容詞" in w[2]:
                A += w[0]
            elif "助動詞" in w[2]:
                if A != "":
                    A += w[0]
                    As.append( (A, "A"))
                    A = ""
        if A != "":
            As.append( ( A, "A"))
        return As        

    def AdvP(self, context):
        AdvPs = []
        for w in context:
            if "副詞" in w[2]:            
                AdvPs.append( ( w[0], "AdvP" ))
        return AdvPs
                        
    def NP(self, w1, w2):
        if len(w1) < 3 or len(w2) < 3:
            return None
        if "名詞" in w1[2] and "助詞" in w2[2]:
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
                return w1[0] + w2[0], "NPmo"
            return w1[0] + w2[0], "NPundef"
        elif "名詞" in w1[2]:
            return w1[0], "N"
        return None


if __name__ == "__main__":
    a = Analysis()
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
    a.analysis("ミズキをイオリが食べた")
    print("="*20)

"""
ミズキ  ミズキ  ミズキ  名詞-一般
が  ガ  が  助詞-格助詞-一般
リンゴ  リンゴ  リンゴ  名詞-一般
を  ヲ  を  助詞-格助詞-一般
食べる  タベル  食べる  動詞-自立   一段    基本形
"""
