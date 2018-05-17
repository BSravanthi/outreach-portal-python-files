var app = angular.module('outreachApp',['ngRoute','outreachApp.controllers','outreachApp.factories']);
app.config(function($routeProvider){
    $routeProvider
	.when('/manage-oc', {
	    templateUrl : '/static/partials/manage-ocs.html',
	    controller  : 'admin-ctrl'
	})
        .when('/workshop-list', {
	    templateUrl : '/static/partials/workshop-list.html',
	    controller  : 'admin-ctrl'
	})
        .when('/nc-users-list', {
	    templateUrl : '/static/partials/nc-users-list.html',
	    controller  : 'admin-ctrl'
	})
	.when('/usage', {
	    templateUrl : '/static/partials/usage-list.html',
	    controller  : 'admin-ctrl'
	})
        .when('/oc-users-list', {
	    templateUrl : '/static/partials/oc-users-list.html',
	    controller  : 'admin-ctrl'
	})
        .when('/edit-oc/:id', {
	    templateUrl : '/static/partials/edit-oc.html',
	    controller  : 'oc-ctrl'
	})
        .when('/documents', {
	    templateUrl : '/static/partials/upload-doc.html',
	    controller  : 'admin-ctrl'
	})
        .when('/profile', {
	    templateUrl : '/static/partials/profile.html',
	    controller  : 'admin-ctrl'
	})
    	.when('/add-oc', {
	    templateUrl : '/static/partials/add-oc.html',
	    controller  : 'admin-ctrl'
        })
	.when('/admin-dashboard', {
	    templateUrl : '/static/partials/admin-dashboard.html',
	    controller  : 'admin-ctrl'
	})
        .when('/add-doc', {
	    templateUrl : '/static/partials/add-doc.html',
	    controller  : 'admin-ctrl'
	})
        .when('/nc-dashboard', {
	    templateUrl : '/static/partials/nc-dashboard.html',
	    controller  : 'nc-dashboard'
	})
        .when('/edit-nc/:id', {
	    templateUrl : '/static/partials/edit-nc.html',
	    controller  : 'edit-nc'
	})
        .when('/manage-workshops', {
	    templateUrl : '/static/partials/manage-workshops.html',
	    controller  : 'manage-workshops'
	})
        .when('/contact-oc', {
	    templateUrl : '/static/partials/contact-oc.html',
	    controller  : 'contact-oc'
	})
        .when('/nc-documents', {
	    templateUrl : '/static/partials/nc-documents.html',
	    controller  : 'nc-documents'
	})
        .when('/nodal-centers', {
	    templateUrl : '/static/partials/nodal-centres.html',
	    controller  : 'nodal-centers'
	})
        .when('/add-workshop', {
	    templateUrl : '/static/partials/add-workshop.html',
	    controller  : 'add-workshop'
        })
        .when('/manage-workshops/pending-action',{
            templateUrl: '/static/partials/pending-workshops.html',
            controller  : 'manage-workshops'
        })
        .when('/manage-workshops/workshop-history',{
            templateUrl: '/static/partials/workshop-history.html',
            controller  : 'manage-workshops'
        })
        .when('/edit-workshop/:id', {
	    templateUrl : '/static/partials/edit-workshop.html',
	    controller  : 'edit-workshop'
	})
        .when('/upload-reports/:id', {
	    templateUrl : '/static/partials/upload-reports.html',
	    controller  : 'upload-reports'
	})
        .when('/oc-upload-reports/:id', {
	    templateUrl : '/static/partials/oc-upload-reports.html',
	    controller  : 'upload-reports'
	})
        .when('/oc-dashboard', {
	    templateUrl : '/static/partials/oc-dashboard.html',
	    controller  : 'oc-dashboard'
	})
        .when('/manage-nc', {
	    templateUrl : '/static/partials/manage-ncs.html',
	    controller  : 'manage-nc'
	})
        .when('/add-nc', {
	    templateUrl : '/static/partials/add-nc.html',
	    controller  : 'add-nc'
	})
        .when('/manage-centres', {
	    templateUrl : '/static/partials/manage-centres.html',
	    controller  : 'manage-centres'
	})
        .when('/add-centre', {
	    templateUrl : '/static/partials/add-centre.html',
	    controller  : 'manage-centres'
	})
        .when('/edit-centre/:id', {
	    templateUrl : '/static/partials/edit-centre.html',
	    controller  : 'edit-centre'
	})
        .when('/oc-manage-workshops', {
	    templateUrl : '/static/partials/oc-manage-workshops.html',
	    controller  : 'oc-manage-workshops'
	})
        .when('/oc-documents', {
	    templateUrl : '/static/partials/oc-docs.html',
	    controller  : 'oc-doclist'
	})
        .when('/oc-manage-workshops/nc-workshops', {
	    templateUrl : '/static/partials/nc-workshops.html',
	    controller  : 'nc-workshops'
	})
        .when('/review-reports/:id', {
	    templateUrl : '/static/partials/review-reports.html',
	    controller  : 'review-reports'
	})
        .when('/view-reports/:id', {
	    templateUrl : '/static/partials/view-reports.html',
	    controller  : 'review-reports'
	})
        .when('/oc-manage-workshops/oc-workshop-history', {
	    templateUrl : '/static/partials/oc-workshop-history.html',
	    controller  : 'oc-workshop-history'
	})
	.when('/ws-list', {
	    templateUrl : '/static/partials/ws_details.html',
	    controller  : 'ws_details'
	})
	.when('/ws-list-offline', {
	    templateUrl : '/static/partials/ws_details_offline.html',
	    controller  : 'ws_details_offline'
	})
	.when('/ws-list/:id', {
	    templateUrl : '/static/partials/detailed_ws_details.html',
	    controller  : 'ws_reports'
	})
	.when('/ws-list-offline/:id', {
	    templateUrl : '/static/partials/detailed_ws_details.html',
	    controller  : 'ws_reports'
	})
	.when('/nc-user-list/:id', {
	    templateUrl : '/static/partials/nc-user-list.html',
	    controller  : 'nc_user_list'
	});
    
    
}
);
