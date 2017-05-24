# -*- coding: utf-8 -*-
"""
Created on Wed May 24 15:21:30 2017

Adapted from:
https://github.com/jcapde/Biterm/blob/master/Biterm_sampler.py
"""

import numpy as np

def gibbs_sampler_LDA(It, V, B, num_topics, b, alpha=1., beta=0.1):
    print("Biterm model ------ ")
    print("Corpus length: " + str(len(b)))
    print("Number of topics: " + str(num_topics))
    print("alpha: " + str(alpha) + " beta: " + str(beta))

    Z =  np.zeros(B,dtype=int)
    Nwz = np.zeros((V, num_topics))
    Nz = np.zeros(num_topics)

    theta = np.random.dirichlet([alpha]*num_topics, 1)
    for ibi, bi in enumerate(b):
        topics = np.random.choice(num_topics, 1, p=theta[0,:])[0]
        Nwz[bi[0], topics] += 1
        Nwz[bi[1], topics] += 1
        Nz[topics] += 1
        Z[ibi] = topics

    for it in range(It):
        print("Iteration: " + str(it))
        Nzold = np.copy(Nz)
        for ibi, bi in enumerate(b):
            Nwz[bi[0], Z[ibi]] -= 1
            Nwz[bi[1], Z[ibi]] -= 1
            Nz[Z[ibi]] -= 1
            pz = (Nz + alpha)*(Nwz[bi[0],:]+beta)*(Nwz[bi[1],:]+beta)/(Nwz.sum(axis=0)+beta*V)**2
            pz = pz/pz.sum()
            Z[ibi] = np.random.choice(num_topics, 1, p=pz)
            Nwz[bi[0], Z[ibi]] += 1
            Nwz[bi[1], Z[ibi]] += 1
            Nz[Z[ibi]] += 1
        print("Variation between iterations:  " + str(np.sqrt(np.sum((Nz-Nzold)**2))))
    return Nz, Nwz, Z

def pbd(doc,names):
    ret = []
    retnames = []
    for term1 in set(doc):
        cnts = 0.
        for term2 in doc:
            if term1 == term2:
                cnts +=1.
        ret.append(cnts/len(doc))
        retnames.append(term1)
    if names:
        return retnames
    else:
        return ret

if __name__=="__main__":
    with open('headlines100K.txt') as f:
        doc=f.read()
        
    vocab_size = 5000
    alpha = 1
    beta = 0.1
    
    headlines = doc.split('\n')
    split = [headline.split(" ") for headline in headlines]
    flat = np.array([word for title in split for word in title if len(word) > 0])
    
    # Get the top vocab_size words
    vocab, counts = np.unique(flat, return_counts=True)
    sort = np.argsort(counts)[-vocab_size:]
    vocab = vocab[sort]
    counts = counts[sort]
    
    btmp = []
    for i, headline in enumerate(split[:100]):
        if (i % 1000 == 0):
            print("Doc {}".format(i))
        if (len(headline) > 0):
            bigrams = []
            for iword1, word1 in enumerate(headline):
                for iword2, word2 in enumerate(headline):
                    if (iword1 < iword2):
                        vi1 = np.where(vocab==word1)[0]
                        vi2 = np.where(vocab==word2)[0]
                        if (len(vi1) > 0 and len(vi2) > 0):
                            bigrams.append((vi1[0],vi2[0]))
            btmp.append(bigrams)
            
    aux = []
    for bi in btmp:
        aux.extend(bi)
    print(b)
    b = aux
    B = len(b)
    bset = set(b)
    num_topics = 10
    pbd_cts = [pbd(doc, False) for doc in btmp]
    pbd_names = [pbd(doc, True) for doc in btmp]
    
    Nz, Nwz, Z = gibbs_sampler_LDA(It=20, V=vocab_size, B=B, num_topics=num_topics, b=b, alpha=alpha, beta=beta)

    topics =  [[vocab[ident] for ident in np.argsort(-Nwz[:,k])[0:10]] for k in range(num_topics)]
    print("TOP 10 words per topic")
    for topic in topics:
         print(topic)
         print("  ---- ")

    thetaz = (Nz + alpha)/(B + num_topics*alpha)
    phiwz = (Nwz + beta)/np.tile((Nwz.sum(axis=0)+vocab_size*beta),(vocab_size,1))

    pzb = [[list(thetaz*phiwz[term[0],:]*phiwz[term[1],:]/(thetaz*phiwz[term[0],:]*phiwz[term[1],:]).sum()) for term in set(doc)] for doc in btmp]

    pdz = []
    for idoc, doc in enumerate(pzb):
        aux = 0
        for iterm, term in enumerate(doc):
            aux += np.array(term) * pbd_cts[idoc][iterm]
        pdz.append(aux)

    pdz = np.array(pdz)

    topics = [[split[ident] for ident in np.argsort(-pdz[:,k])[0:5]] for k in range(num_topics)]
    print("TOP 5 tweets per topic")
    for topic in topics:
        for tweet in topic:
            print(tweet)
        print(" ---- ")