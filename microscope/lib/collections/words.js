var logger = new Logger('collections:WordManager');

Logger.setLevel('collections:WordManager', 'trace');
// Logger.setLevel('collections:WordManager', 'debug');
// Logger.setLevel('collections:WordManager', 'info');
// Logger.setLevel('collections:WordManager', 'warn');

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
    this.highlightsPurpose = [];
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
            if (type === "Purpose") {
                logger.debug("Adding " + userID + " to highlightsPurpose for " + wordID);
                Words.update({_id: wordID},{$addToSet: {highlightsPurpose: userID}});
                Words.update({_id: wordID},{$pull: {highlightsMechanism: userID}});
            } else if (type === "Mechanism") {
                logger.debug("Adding " + userID + " to highlightsMechanism for " + wordID);
                Words.update({_id: wordID},{$pull: {highlightsPurpose: userID}});
                Words.update({_id: wordID},{$addToSet: {highlightsMechanism: userID}});
            } else {
                logger.debug("Neither: un-annotating");
                Words.update({_id: wordID},{$pull: {highlightsPurpose: userID}});
                Words.update({_id: wordID},{$pull: {highlightsMechanism: userID}});
            }
            return true;
        }
    }
}());