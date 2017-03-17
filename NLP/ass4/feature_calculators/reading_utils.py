import os
#functions to excess sentence and entity data

chunks_dict = dict()

# returns index of entry in sentence(starting from zero)
# if first is false , will return index of last word of entry(e.g index of 'america' in entry 'united states of america'
def entry_index( ent, first=True):
    if first:
        return ent['entries'][0].position
    return ent['entries'][-1].position


def get_lemma(sent , index):
    return sent['entries'][index].lemma

#head word of ent
def get_head( entity):
    entity_indexes = entity['entries'][0]

    for word in entity['entries']:
        head_id = word.head
        is_head = True
        #head word is a word who's head is not part of the NP chunk.
        for other_word in entity['entries']:
            if other_word.id == head_id:
                is_head = False ; break
        if is_head:
            return word.lemma



def get_entry(idx, sent):
    for e in sent['entries']:
        if int(e.id) == idx:
            return e



def getDependentWords(idx, sent):
    d = []
    for e in sent['entries']:
        if e.head == idx:
            d.append(e.word)
    return d
        
