
// Global reference to the map object
var map;

// Stores the loaded json with the sites
var sites_geojson;

// Sidebar objects
var leftbar;
var rightbar;

// UI controls
var btn_sitelist;

// Initializes the map and triggers and loads the sites.
function init_uristmaps() {
    map = L.map('map').setView([0, 0], 3);
    L.tileLayer('/tiles/{z}/{x}/{y}.png', {
        noWrap: true,
        maxZoom: 7,
        attribution: "<a href='http://www.uristmaps.org/'>UristMaps " + urist_version + "</a>",
    }).addTo(map);

    // Load the sites json containing short info for every site
    jQuery.getJSON("/js/sites.json", process_loaded_sites);
    
    setup_sidebars();
    init_buttons();
};

function init_buttons() {
    btn_sitelist = L.easyButton("fa-bars",
        btn_sitelist_clicked,
        "Show list of sites");

    btn_legend = L.easyButton("fa-question-circle",
        btn_legend_clicked,
        "Show legend for the current overlay","");
    btn_legend.options.position = "bottomright";
    map.addControl(btn_legend);
};

function setup_sidebars() {
    leftbar = L.control.sidebar("sidebar-left", {
        position: "left",
	autoPan: false,
    });
    rightbar = L.control.sidebar("sidebar-right", {
        position: "right",
	autoPan: false,
    });

    map.addControl(leftbar);
    map.addControl(rightbar);
};

function btn_sitelist_clicked() {
    leftbar.toggle();
}

function btn_legend_clicked() {
    rightbar.toggle();
}

function process_loaded_sites(data) {
    sites_geojson = data;
  
    // Create a cluster group to better show the site icons
    var clusters = new L.MarkerClusterGroup();

    // Convert geojson info to clustered markers
    var points = L.geoJson(null, {
        pointToLayer: function (feature, latlng) {
            var marker = L.marker(latlng, {icon: get_icon(feature.properties.img)});
            if (feature.properties && feature.properties.popupContent) {
                marker.bindPopup(feature.properties.popupContent);
            }
            clusters.addLayer(marker);
            return clusters;
        }
    });
    $.each(data.features, function(fid, feature) {
        points.addData(feature);
    });
    map.addLayer(clusters);
    
    // Add 
    var icon_layer = {"Sites": clusters};
    L.control.layers({}, icon_layer).addTo(map);
};

$(function() {
    $(".site-btn").click(function() {
        var lat = $(this).attr("data-lat");
        var lon = $(this).attr("data-lon");
        map.fitBounds([[lat,lon],[lat+0.01, lon+0.01]]);
    });
});
