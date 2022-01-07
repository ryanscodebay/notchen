const axios = require('axios');
//Place for all the various API calls
module.exports = {  
  //Yandex Translation API
  translate: function (yandex_api_key,content,msg){
    axios.get('https://translate.yandex.net/api/v1.5/tr.json/translate', {
      params: {
        key: yandex_api_key,
        text: content,
        lang: 'en',
        options: 1
      }
    }).then(res => {
      if (res.data.text[0] !== content) {
        // make the response pretty, provides iso 2 code and translation
        msg.reply('Language Detected: ' + res.data.detected.lang + "\n\"" + res.data.text[0] + "\"");
      }
    });
  }

  // other api calls
};
