const express = require('express');
const cors = require('cors');
const fs = require('fs');
const { spawn } = require('child_process');
const app = express();
const port = 3000;

app.get('/get-data', (req, res) => {
    const scriptPath = '../../dbext.py';
    const id = req.query.id;

    // Check if the file exists
    if (!fs.existsSync(scriptPath)) {
        console.error('Python script not found at path:', scriptPath);
        return;
    }

    const python = spawn('python3', [scriptPath, id]);
    let dataToSend;

    python.stdout.on('data', (data) => {
        console.log('Pipe data from python script ...');
        dataToSend = data.toString();
    });

    python.on('close', (code) => {
        console.log(`child process close all stdio with code ${code}`);
        res.setHeader('Access-Control-Allow-Origin', 'chrome-extension://klnldgenohnbnfddnccjehnhmnbfkchp');
        res.json({ message: dataToSend });
    });
});

app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});