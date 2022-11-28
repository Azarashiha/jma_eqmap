//https://docs.mapbox.com/mapbox-gl-js/example/add-image/
mapboxgl.accessToken = 'pk.eyJ1IjoiYXphcmFzaGkiLCJhIjoiY2t0YmdibXczMXZwbzJubzBnZHI4Ym4zMCJ9.1C3RNiQqSioL1NkDSFE5Xg';
    
var map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/azarashi/cktbgkxip5jml17n06wvzmgj9',
    center: [139.7670516, 35.6811673],//仮数値
    zoom: 7,//仮数値
    //bounds:addpoint(),
    projection: 'globe',
    customAttribution: ['<a href="https://www.jma.go.jp/jma/index.html">震度情報:©︎気象庁</a>', '<a href="https://nlftp.mlit.go.jp/index.html">国土数値情報:©︎国土交通省</a>','<a href="https://twitter.com/nyaonearthquake?s=21">編集:©︎nyaonearthquake</a>'],

});

// コントロール関係表示
map.addControl(new mapboxgl.NavigationControl());
var citydata;
//マウスクリック時にポップアップを出すか
var popup = new mapboxgl.Popup({
    closeButton: true
});

//ボタン要素を取得------
let switchBtn = document.getElementsByTagName('button')[0];
//表示・非表示を切り替える要素を取得
let box = document.getElementById('box');

//styleのdisplayを変更する関数
let changeElement = (el)=> {

  if(el.style.display==''){
    el.style.display='none';
  }else{
    el.style.display='';
  }

}
//=========================

var url = 'data/jma_area(sample).json'//'jma_area_e.json'//'https://example.com/x.json';
$.getJSON(url, function(data){
    areadata=data
});
var url = 'data/jma_city(sample).json'//'jma_area_e.json'//'https://example.com/x.json';
$.getJSON(url, function(data){
    citydata=data
});
map.on("load", function () {
    map.addControl(new mapboxgl.Minimap({
center: [139.7670516, 35.6811673],//[areadata['features'][1]['geometry']['coordinates'][0], areadata['features'][1]['geometry']['coordinates'][1]],
style: 'mapbox://styles/azarashi/cladgnrdz000315qmj9d3q6iu',
zoom: 2,
zoomLevels: []
}), 'bottom-left');})


//レスポンシブ(横640px)
var mobile = $(window).width() < 540;
    

    
map.on('load', function () {
    
//console.log('data : ', data);
console.log('areaデータの数 '+areadata['features'].length)//geojson長さ
console.log('cityデータの数 '+citydata['features'].length)//geojson長さ

console.log(areadata['features'][0]['geometry']['coordinates'][0])

imgfile='data/img/v_1'
map.loadImage(`${imgfile}/epicenter.png`, (error, image) => {
    if (error) throw error;
    if (!map.hasImage('epicenter')) map.addImage('epicenter', image);
    
}),
map.loadImage(`${imgfile}/int1.png`, (error, image) => {
    if (error) throw error;
    if (!map.hasImage('1')) map.addImage('1', image);
}),
map.loadImage(`${imgfile}/int2.png`, (error, image) => {
    if (error) throw error;
    if (!map.hasImage('2')) map.addImage('2', image);
}),
map.loadImage(`${imgfile}/int3.png`, (error, image) => {
    if (error) throw error;
    if (!map.hasImage('3')) map.addImage('3', image);
}),
map.loadImage(`${imgfile}/int4.png`, (error, image) => {
    if (error) throw error;
    if (!map.hasImage('4')) map.addImage('4', image);
}),
map.loadImage(`${imgfile}/int5l.png`, (error, image) => {
    if (error) throw error;
    if (!map.hasImage('5-')) map.addImage('5-', image);
}),
map.loadImage(`${imgfile}/int5h.png`, (error, image) => {
    if (error) throw error;
    if (!map.hasImage('5+')) map.addImage('5+', image);
}),
map.loadImage(`${imgfile}/int6l.png`, (error, image) => {
    if (error) throw error;
    if (!map.hasImage('6-')) map.addImage('6-', image);
}),
map.loadImage(`${imgfile}/int6h.png`, (error, image) => {
    if (error) throw error;
    if (!map.hasImage('6+')) map.addImage('6+', image);
}),
map.loadImage(`${imgfile}/int7.png`, (error, image) => {
    if (error) throw error;
    if (!map.hasImage('7')) map.addImage('7', image);
}),


map.addSource('data', {
    'type': 'geojson',
    'data': areadata,
    maxzoom: 10,
    });
// ポイントソース設定
map.addSource('vt', {
    promoteId: "N03_007",
    'type': 'vector',
    'tiles': ['https://azarashiha.github.io/vt/{z}/{x}/{y}.pbf'],//['https://weatherbox.github.io/warning-area-vt/v2/{z}/{x}/{y}.pbf']
    //"https://weatherbox.github.io/warning-area-vt/v2/{z}/{x}/{y}.pbf"
    
});
//https://labs.mapbox.com/education/impact-tools/data-joins/
for (const feature of citydata.features){
    const id=feature.properties.code;
    const c=feature.properties.class;
    map.setFeatureState(
        {
            'source':'vt',
            'sourceLayer':'city',
            'id': id,
        },
        {
            'class':c
        }
    )
}
map.addLayer({
    'id': 'pref-line',
    'type': 'fill',
    'source': 'vt',
    'source-layer': 'city',
    'paint': {
        //https://www.w3schools.com/css/css_colors_rgb.asp
        'fill-color': [
            'match',
            ['feature-state','class'],
            '1',
            'rgba(171,223,244,0.7)',
            '2',
            'rgba(115,189,105,0.7)',
            '3',
            'rgba(227,227,80,0.7)',
            '4',
            'rgba(249,162,65,0.7)',
            '5-',
            'rgba(239,57,59,0.7)',
            '5+',
            'rgba(239,57,59,0.7)',
            '6-',
            'rgba(161,23,23,0.7)',
            '6+',
            'rgba(161,23,23,0.7)',
            '7',
            'rgba(56,1,13,0.7)',
            'rgba(128,128,128,0.2)',

        ],
        'fill-opacity': 0.9,
        'fill-outline-color': 'rgba(82,82,82, 0.4)'//'rgba(200, 100, 240, 1)'
        }
    
    });

//epicenterのみ先述    
map.addLayer({
    'id':'epicenter',
    'type':'symbol',
    'source':'data',
    'filter': ['==', 'class', 'epicenter'],
    'layout':{
        'icon-image': 'epicenter',//`${symbol}`,
        'icon-allow-overlap': true,
        'icon-size': 1.5
    },
    //'filter': ['==', 'class', symbol]
});

    //参考：https://docs.mapbox.com/mapbox-gl-js/example/filter-markers/
    for (const feature of areadata.features){
    const symbol = feature.properties.class;
    const layerID = `${symbol}`;
    
    
    

    if(!map.getLayer(layerID)){
        console.log(layerID);
        map.addLayer({
            'id':`${layerID}`,
            'type':'symbol',
            'source':'data',
            'filter': ['==', 'class', symbol],
            'layout':{
                'icon-image': `${symbol}`,
                'icon-allow-overlap': true,
                'icon-size': 0.5
            },
            //'filter': ['==', 'class', symbol]
        });

        
        
        
    }

    
    
    
    }
    
    // 指定位置にズーム
//const center=(data['features'][0]['geometry']['coordinates']);
//console.log('center'+center);

function addpoint(){
    let array =[];
    for(let i=0;i<=areadata['features'].length;i++){
        //console.log(data['features'][i]['geometry']['coordinates']);
        
        let j=areadata['features'][i]['geometry']['coordinates']
        array.push(j);
        //console.log(array);
        if (i==(areadata['features'].length-1)){
            return array
        }
    }
}
//マーカーの位置に応じて最適なzoomを決める
//console.log(addpoint())
//map.fitBounds(addpoint(), {padding: 320,animate: false},);
console.log(areadata['features'].length)
var line = turf.lineString(addpoint());
var bbox = turf.bbox(line); 
if(areadata['features'].length>7){
    map.fitBounds(bbox, {padding: 100,animate: false},)
    console.log("7以上")
}else if(areadata['features'].length>4){
    map.fitBounds(bbox, {padding: 250,animate: false},)
    console.log("4以上")    
}else{//データ数によって見づらいならないように
    map.fitBounds(bbox, {padding: 360,animate: false},)
    //近すぎると見ずらいから   
    console.log("else")
}



//以下試験的に書いたプログラムなので無視してください。
//===================

 // レイヤ設定
 var Map_AddLayer = {
    epicenter: "震源地",
    '7': "震度7",
    '6+': "震度6強",
    '6-': "震度6弱",
    '5+': "震度5強",
    '5-': "震度5弱",
    '4': "震度4",
    '3': "震度3",
    '2': "震度2",
    '1': "震度1",
    
    
    
};


// レイヤメニュー作成
for (var i = 0; i < Object.keys(Map_AddLayer).length; i++) {
    // レイヤID取得
    var id = Object.keys(Map_AddLayer)[i];
    // aタグ作成
    var link = document.createElement("a");
    link.href = "#";
    // id追加
    link.id = id;
    // 名称追加
    link.textContent = Map_AddLayer[id];

    // 初期表示全て表示
    link.className = "active";

    // aタグクリック処理
    link.onclick = function (e) {
        // id取得
        var clickedLayer = this.id;
        e.preventDefault();
        e.stopPropagation();

        // ON/OFF状態取得
        var visibility = map.getLayoutProperty(clickedLayer, "visibility");

        // ON/OFF判断
        if (visibility === 'visible') {
            // クリックしたレイヤを非表示
            map.setLayoutProperty(clickedLayer, 'visibility', 'none');
            this.className = '';
        } else {
            // クリックしたレイヤを表示
            map.setLayoutProperty(clickedLayer, 'visibility', 'visible');
            this.className = 'active';
        }
    };

    // レイヤメニューにレイヤ追加
    //var layers = document.getElementById("menu");
    //layers.appendChild(link);
}





//===================
});



map.on('mousemove', (e) => {
    //zoomレベル確認
    //console.log('zoom: ' + map.getZoom());
    var features = map.queryRenderedFeatures(e.point);
    // Limit the number of properties we're displaying for
    // legibility and performance
    const displayProperties = [
        'type',
        'properties',
        'id',
        'layer',
        'source',
        'sourceLayer',
        'state'
        ];
        
        const displayFeatures = features.map((feat) => {
        const displayFeat = {};
        displayProperties.forEach((prop) => {
        displayFeat[prop] = feat[prop];
        });
        return displayFeat;
        });
        
        // Write object as string with an indent of two spaces.
        document.getElementById('features').innerHTML = JSON.stringify(
        displayFeatures,
        null,
        2
    );
})
