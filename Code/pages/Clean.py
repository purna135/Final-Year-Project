import pandas as pd
# import numpy as np
# import nltk
import re
# from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
# import math
import enchant
from stemming.porter2 import stem
import pathConfig as pc

#--------------------------------
###Path 
pathStopwords = pc.PATH_CONFIG['pathStopWords']
pathData = pc.PATH_CONFIG['pathData']
#-------------------------------


class DataCLean:

    def extract(self, path):
        fd = open(path, encoding="utf-8", errors='replace')
        df = pd.read_csv(fd)
        defined = df['class'] != ("undefined")
        # #output dataframe without undeined
        df2 = df[defined]
        defined1 = df2['class'] != "Undefined"
        df4 = df2[defined1]
        # replace no PI with no
        df3 = df4.replace("No PI", "no")
        # replace PI with yes
        final = df3.replace("PI", "yes")

        replace_yes = final.replace("Yes", "yes")
        final_df = replace_yes.replace("No", "no")
        return final_df, df

    def text_concat(self, final_df):
        text = ""
        for x in final_df["text"]:
            text = text + str(x)
        return text

    def read_stopwords(self, path):
        with open(path, "r") as file1:
            stopword = file1.readlines()
        return stopword[0].split()


    def removeStopWords(self,text):
        # stop_words = set(stopwords.words('english'))
        stop_words = self.read_stopwords(pathStopwords)
        word_tokens = word_tokenize(text)
        return [w.lower() for w in word_tokens if w not in stop_words]

    def remove_stopwords(self, df_punc_remove):
        # stop_words = set(stopwords.words('english'))
        li_stopwords = self.read_stopwords(pathStopwords)
        for count_clean, text in enumerate(df_punc_remove['text']):
            word_tokens = word_tokenize(text)
            clean_text = ""
            for w in word_tokens:
                if w.lower() not in li_stopwords:
                    clean_text = clean_text + w.lower() + ' '
            df_punc_remove.at[count_clean, 'text'] = clean_text
            df_punc_remove.at[count_clean, 'class'] = df_punc_remove.iloc[count_clean]['class']
        # return list of corpus without stop words in a list.
        # print(df_punc_remove)
        return df_punc_remove

    def removePunc(self, eachText):
        return re.sub(r'[^\w\s]', '', eachText)
        # pattern = re.compile(r'[a-zA-Z]+')
        # matches = pattern.finditer(eachText)
        # new_corpus = ""
        # for match in matches:
        #     new_corpus = new_corpus + match.group() + " "
        # return new_corpus

    def remove_punc(self, temp_df):
        for count, text in enumerate(temp_df['text']):
            out = re.sub(r'[^\w\s]', '', text)
            temp_df.at[count,'text'] = out
            temp_df.at[count, 'class'] = temp_df.iloc[count]['class']
        return temp_df

    def space(self, final_df):
        new_df = pd.DataFrame()
        for count_tweets, text in enumerate(final_df['text']):
            temp = ""
            for char in text:
                temp = temp + ' ' + char if char in [",",".","!","?",":",";"] else temp + char
            # print(temp)
            new_df.at[count_tweets, 'text'] = temp
            new_df.at[count_tweets, 'class'] = final_df.iloc[count_tweets]['class']
        # print("new_df")
        # print(new_df)
        return new_df

    def handle_negation(self, final_df):
        out_df = pd.DataFrame()
        count = 0
        for count_tweet, text in enumerate(final_df['text']):
            temp_text = ""
            li_text = text.split()
            for word in li_text:
                lower_word = word.lower()
                temp_text = temp_text + word + " "
                if lower_word in ["didn't", "not", "no", "never", "don't", "hate"]:
                    temp = count + 1
                    for i in range(temp,len(li_text)):
                        if li_text[i] in [",","?","!","."]:
                            temp_text = " "+temp_text + li_text[i] + " "
                            break
                        else:
                            temp_text = temp_text + "NOT_" + li_text[i]+" "

            # print(temp_text)
            out_df.at[count_tweet, 'text'] = temp_text
            out_df.at[count_tweet,'class'] = final_df.iloc[count_tweet]['class']
        return out_df

    def check_english(self, temp_df):
        d = enchant.Dict("en_US")
        new_eng = pd.DataFrame()
        for count, sentence in enumerate(temp_df['text']):
            temp_sent = ""
            for word in sentence.split():
                temp = word.lower()
                if d.check(word):
                    # print("ammar")
                    temp_sent = temp_sent + temp + " "
            # print(temp_sent)
            new_eng.at[count,'text'] = temp_sent
            new_eng.at[count, 'class'] = temp_df.iloc[count]['class']
        # print(new_eng)
        return new_eng

    def Stemming(self, temp_df):
        new_eng = pd.DataFrame()
        for count, sentence in enumerate(temp_df['text']):
            temp_sent = ""
            for word in sentence.split():
                temp = stem(word.lower())
                temp_sent = temp_sent + temp + " "
            # print(temp_sent)
            new_eng.at[count, 'text'] = temp_sent
            new_eng.at[count, 'class'] = temp_df.iloc[count]['class']
        # print(new_eng)
        return new_eng

        # stem("factionally")

    def clean_data(self, final_df):
        # print(final_df)
        eng_df = self.check_english(final_df)
        # print(eng_df)
        df_stem = self.Stemming(eng_df)
        new_df = self.space(eng_df)
        new_corpus_df = self.handle_negation(new_df)
        remove_punc_df = self.remove_punc(new_corpus_df)
        df_remove_stopWords = self.remove_stopwords(remove_punc_df)

        new_corpus = self.text_concat(df_remove_stopWords)
        li_new_corpus = new_corpus.split()
        # print(remove_punc_df)
        return li_new_corpus, df_remove_stopWords

    def make_unique_li(self, li_cleanText):
        unique_words_set = set(li_cleanText)
        return list(unique_words_set)

    def stemmed(self,li_cleanText):
        for count_stemed, word in enumerate(li_cleanText):
            if word[-1] == "s":
                li_cleanText[count_stemed] = word[:-1]
            elif word[-2:] == "ed":
                li_cleanText[count_stemed] = word[:-2]
            elif word[-3:] == "ing":
                li_cleanText[count_stemed] = word[:-3]
        return li_cleanText

    def Clean(self):
        final_df, df = self.extract(pathData)
        # corpus = clean.text_concat(final_df)
        li_clean_text, df_clean = self.clean_data(final_df)
        # print("ammar")
        uniqueWords = self.make_unique_li(li_clean_text)
        return df_clean, uniqueWords
