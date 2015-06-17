Router.configure({
  layoutTemplate: 'layout',
  loadingTemplate: 'loading',
  waitOn: function() { 
    return [
        Meteor.subscribe('posts'),
        Meteor.subscribe('documents'),
        Meteor.subscribe('sentences'),
        Meteor.subscribe('words')
    ];
  }
});

Router.map(function() {
    
    this.route('/', {name: 'postsList'});

    this.route('/posts/:_id', {
        name: 'postPage',
        data: function() { return Posts.findOne(this.params._id); }
    });

    this.route('Annotate', {
        name: 'Annotate',
        path: '/annotate',
        template: 'annotationPage',
        data: function() { 
            // later we will call the DocumentFactory function
            // to serve up a random document
            return Documents.findOne();
        },
    })

})