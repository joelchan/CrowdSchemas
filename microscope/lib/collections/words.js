Words = new Mongo.Collection('words');

Word = function (content, sequence, sentence) {

    this.sentenceID = sentence._id;
    this.docID = sentence.docID;

    // the word (string)
    this.content = content;

    // the word's position in the sentence
    this.sequence = sequence;

    // highlights - array of userIDs
    // who have highlighted this word
    this.highlightsProblem = [];
    this.highlightsMechanism = [];
}