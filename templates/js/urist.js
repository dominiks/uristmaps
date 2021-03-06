
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
        maxZoom: {{ max_zoom }},
        attribution: "<a href='http://www.uristmaps.org/'>UristMaps {{ version }}</a>",
    }).addTo(map);
    window.map = map;

    // Load the sites json containing short info for every site
    jQuery.getJSON("/js/sitesgeo.json", process_loaded_sites);
    
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

/**
 * Event handler for onclick of toggle detail map button in
 * sites' tooltip.
 */
function toggle_detailed_map(site_id) {
    var overlay = window.active_site_maps[site_id];

    // When the overlay was active, remove it
    if (overlay != undefined) {
        window.map.removeLayer(overlay);
        window.active_site_maps[site_id] = null;
    } else {
        // Create the overlay and add it to active_site_maps
        var image_url = "/sites/" + site_id + ".png";

        // the .features object is a list in which the index is resolved as id-1
        for (var i = 0; i < window.sites_geojson.features.length; i++) {
            var site = window.sites_geojson.features[i];
            if (site.properties.id != site_id) {
                continue;
            }
            var overlay = L.imageOverlay(image_url, site.properties.map_bounds);
            window.active_site_maps[site_id] = overlay;
            overlay.addTo(window.map);
            break;
        }
    }
}

/**
 * When the sites json is loaded, create the cluster group for 
 * all site markers.
 */
function process_loaded_sites(data) {
    sites_geojson = data;
    window.sites_geojson = data;
    window.active_site_maps = {};
  
    // Create a cluster group to better show the site icons
    var clusters = new L.MarkerClusterGroup({
        maxClusterRadius: {{ max_cluster_radius }}
    });

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
