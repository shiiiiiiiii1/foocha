var fs = require('fs')
const SiRuDevice = require('skyway-siru-device')

const device = new SiRuDevice('testroom')

device.on('connect', () => {
  // publish timestamp data every 1 seconds.
  setInterval(ev => {
    fs.readFile('LatLng.json', 'utf8', (error, text) => {
      var json_obj = JSON.parse(text || 'null')
      console.log(typeof(json_obj))
      // var send_ob = 
      device.publish('timestamp', json_obj)
    })
  }, 1000)
})

// handle GET /echo request from client
device.get('/echo/:message', (req, res) => {
  res.send(req.params.message)
})
