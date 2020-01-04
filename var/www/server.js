var http = require('http');
var express = require('express');
var fs = require('fs');

var app = express();

app.use(express['static'](__dirname));

const homeDir = "/home/pi/autowx2";
const wwwRootDir = "/var/www";
const wwwDir = homeDir + wwwRootDir;
const loggingDir = "/recordings/logs"
const staticDir = "/css";
const nextPassShort = wwwDir + "/nextpassshort.tmp";
const mainIndexTemplate = homeDir + "/var/flask/node_templates/index.html";

function renderTemplate(templateFile, title, body, response) {
    var html = "";
    try {
        html = fs.readFileSync(templateFile, "utf8");
    } catch (e) {
        response.status(500).send({
            internal_error: e
        });
        return;
    }

    html = html.replace(/{{title}}/gi, title);
    html = html.replace(/{{body}}/gi, body);

    html = html.replace(/{{static_dir}}/gi, staticDir);
    html = html.replace(/{{www_dir}}/gi, wwwRootDir);

    response.status(200).send(html);
}

app.use(express.static(wwwRootDir), function (req, res, next) {
    // Uncomment the line below to view the entire URL calling the API.
    // console.log("Incoming request: " + req.originalUrl);
    next();
});

app.get('/', function (req, res) {
    // Check pass list file exists
    var fileExists = true;
    try {
        fileExists = fs.existsSync(nextPassShort);
    } catch {
        fileExists = false;
    }

    var body = ""
    if (fileExists) {
        // next pass table
        try {
            // Reading a file may throw
            var nextPassHtmlShort = fs.readFileSync(nextPassShort);
            body += "<h3>Next passes</h3><span id='nextPassWindow'>" + nextPassHtmlShort + "</span>";
        } catch (e) {
            console.log(e);
            body += "<p>Failed to load the next passes.</p>";
        }
    } else {
        body = "<p>File containing the next passes could not be found.</p>"
    }

    renderTemplate(mainIndexTemplate, title = "Home page", body = body, res);
});

// The RPI doesn't handle showing the contents of a directory as a response. We
// need to generate our own.
app.get('/recordings/logs/', function (req, res) {
    // Check pass list file exists
    var bodyHtml = "<h3>All logs</h3>"
    var files = fs.readdirSync(wwwDir + loggingDir);
    if (files != undefined && files.length) {
        // Generate the HTML list of log files
        for (var i = (files.length - 1); i >= 0; i--) {
            bodyHtml += "<a href=\"" + loggingDir + "/" + files[i] + "\">" + files[i] + "</a></br>";
        }
    }
    renderTemplate(mainIndexTemplate, title = "All logs", body = bodyHtml, res);
});

// Express route for any other unrecognised incoming requests
app.get('*', function (req, res) {
    res.status(404).send({
        error: 'Unrecognised API call: ' + req.originalUrl
    });
});

app.use(function (err, req, res, next) {
    if (req.xhr) {
        res.status(500).send({
            error: 'Oops! Something went wrong!'
        });
    } else {
        next(err);
    }
});


app.listen(3000);
console.log('App Server running on port 3000');


// -----------
// Determine the local IP address of the RPI


'use strict';

var os = require('os');
var ifaces = os.networkInterfaces();

Object.keys(ifaces).forEach(function (ifname) {
    var alias = 0;

    ifaces[ifname].forEach(function (iface) {
        if ('IPv4' !== iface.family || iface.internal !== false) {
            // skip over internal (i.e. 127.0.0.1) and non-ipv4 addresses
            return;
        }

        if (alias >= 1) {
            // this single interface has multiple ipv4 addresses
            console.log(ifname + ':' + alias, iface.address);
        } else {
            // this interface has only one ipv4 adress
            console.log(ifname, iface.address);
        }
        ++alias;
    });
});