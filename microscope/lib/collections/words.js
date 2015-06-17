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

WordManager = (function() {
    return {
        markWord: function(wordID, userID, type) {
            /******************************************************************
             * Mark the word with appropriate annotation for that user
             * @params
             *    wordID - the id of the word being annotated
             *    userID - the user making the annotation
             *    type (str) - problem, mechanism, or neither
             *****************************************************************/
            return true;
        }
    }
}());