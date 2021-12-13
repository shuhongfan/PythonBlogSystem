var vm = new Vue({
    el: '#app',
    // 修改Vue变量的读取语法，避免和django模板语法冲突
    delimiters: ['[[', ']]'],
    data: {
        host,
        show_menu:false,
        data_config:'{"skin": "moono-lisa", "toolbar_Basic": [["Source", "-", "Bold", "Italic"]], "toolbar_Full": [["Styles", "Format", "Bold", "Italic", "Underline", "Strike", "SpellChecker", "Undo", "Redo"], ["Link", "Unlink", "Anchor"], ["Image", "Flash", "Table", "HorizontalRule"], ["TextColor", "BGColor"], ["Smiley", "SpecialChar"], ["Source"]], "toolbar": "Custom", "height": "250px", "width": "auto", "filebrowserWindowWidth": 940, "filebrowserWindowHeight": 725, "tabSpaces": 4, "toolbar_Custom": [["Smiley", "CodeSnippet"], ["Bold", "Italic", "Underline", "RemoveFormat", "Blockquote"], ["TextColor", "BGColor"], ["Link", "Unlink"], ["NumberedList", "BulletedList"], ["Maximize"]], "extraPlugins": "codesnippet,prism,widget,lineutils", "language": "en-us"}',
        username:'',
        is_login:false,
    },
    mounted(){
        this.username=getCookie('username');
        this.is_login=getCookie('is_login');
    },
    methods: {
        //显示下拉菜单
        show_menu_click:function(){
            this.show_menu = !this.show_menu ;
        },
    }
});
