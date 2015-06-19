var logger = new Logger('Client:land');

Logger.setLevel('Client:land', 'trace');
// Logger.setLevel('Client:land', 'debug');
// Logger.setLevel('Client:land', 'info');
// Logger.setLevel('Client:land', 'warn');

Template.land.events({
    'click .continue' : function() {
        logger.debug("User clicked continue");

        if (Meteor.user()) {
            logger.trace("Sending user to tutorial");
            Router.go("Tutorial");    
        } else {
            alert("Please sign in or create an account (in the menu in the top right-hand corner of the page) before continuing");
        }   
    }
});