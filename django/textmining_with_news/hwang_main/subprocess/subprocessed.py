import MeCab

class Subprocessed():
    def execution(value):
        m = MeCab.Tagger('-d C:\mecab\mecab-ko-dic')
        tag_classes = ['NNG', 'NNP','VA', 'VV+EC', 'XSV+EP', 'XSV+EF', 'XSV+EC', 'VV+ETM', 'MAG', 'MAJ', 'NP', 'NNBC', 'IC', 'XR', 'VA+EC']
        result = ''
        value = m.parseToNode(value)
        print(value)
        while value:
            tag = value.feature.split(",")[0]
            word = value.feature.split(",")[3]
            if tag in tag_classes:
                if word == "*": value = value.next
                result += word.strip()+" "
                #print(word.strip(), type(word.strip()), tag)
            value = value.next
        return result
