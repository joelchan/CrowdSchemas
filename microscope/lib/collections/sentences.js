Sentences = new Mongo.Collection('sentences');

Sentence = function(docID, content, psn) {

    this.docID = docID;
    this.psn = psn;

    this.content = content;

    // array of word ids
    this.wordIDs = [];
}

SentenceFactory = (function() {
    return {
        createDummy: function(docID, content, psn) {
            var sent1 = new Sentence(docID, content, psn);
            var sent1ID = Sentences.insert(sent1);
            sent1 = Sentences.findOne({_id: sent1ID});
            var words = sent1.content.split(" ");
            var wordIDs = [];
            for (i=0; i < words.length; i++) {
              var word = new Word(words[i], i+1, sent1);
              wordID = Words.insert(word);
              wordIDs.push(wordID);
            }
            Sentences.update({_id: sent1ID},{$push: {wordIDs: wordIDs}});
        },
    };
}());