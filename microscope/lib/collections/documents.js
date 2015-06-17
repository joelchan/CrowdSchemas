Documents = new Mongo.Collection('documents');

Document = function(fileName) {

    this.title = fileName;

    // array of sentence IDs
    this.sentences = [];

    // array of userIDs that have seen this document
    // and made at least one annotation
    this.annotatedBy = [];
}

DocumentManager = (function() {
    return {
        sampleDocument: function(userID) {
            /******************************************************************
             * Sample a document for a given user to annotate
             * @params
             *    userID - the id of the user we want to serve
             *****************************************************************/
        }
    }
}());