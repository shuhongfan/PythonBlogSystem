var vm = new Vue({
    el: '#app',
    // 修改Vue变量的读取语法，避免和django模板语法冲突
    delimiters: ['[[', ']]'],
    data: {
        host,
        show_menu:false,
        mobile:'',
        mobile_error:false,
        mobile_error_message:'手机号错误',
        password:'',
        password_error:false,
        password_error_message:'密码错误',
        password2:'',
        password2_error:false,
        password2_error_message:'密码不一致',
        uuid:'',
        image_code:'',
        image_code_error:false,
        image_code_error_message:'图片验证码错误',
        sending_flag:false,
        image_code_url:''
    },
    mounted(){
        this.generate_image_code()
    },
    methods: {
        //显示下拉菜单
        show_menu_click:function(){
            this.show_menu = !this.show_menu ;
        },
        generateUUID: function () {
            var d = new Date().getTime();
            if (window.performance && typeof window.performance.now === "function") {
                d += performance.now(); //use high-precision timer if available
            }
            var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
                var r = (d + Math.random() * 16) % 16 | 0;
                d = Math.floor(d / 16);
                return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
            });
            return uuid;
        },
        // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
        generate_image_code: function () {
            // 生成一个编号 : 严格一点的使用uuid保证编号唯一， 不是很严谨的情况下，也可以使用时间戳
            this.uuid = this.generateUUID();
            // 设置页面中图片验证码img标签的src属性
            this.image_code_url = this.host + "/imagecode/?uuid=" + this.uuid;
        },
        //检查手机号
        check_mobile: function(){
            var re = /^1[3-9]\d{9}$/;
            if (re.test(this.mobile)) {
                this.mobile_error = false;
            } else {
                this.mobile_error = true;
            }
        },
        //检查密码
        check_password:function () {
            var re = /^[0-9A-Za-z]{8,20}$/;
            if (re.test(this.password)) {
                this.password_error = false;
            } else {
                this.password_error = true;
            }

        },
        //检查确认密码
        check_password2:function () {
            if (this.password != this.password2) {
                this.password2_error = true;
            } else {
                this.password2_error = false;
            }
        },
        //检查验证码
        check_image_code:function () {
            if (!this.image_code) {
                this.image_code_error = true;
            } else {
                this.image_code_error = false;
            }
        },
        //提交
        on_submit:function () {
            this.check_mobile();
            this.check_password();
            this.check_password2();

            if (this.mobile_error == true || this.password_error == true || this.password2_error == true
                || this.image_code_error == true ) {
                // 不满足注册条件：禁用表单
                window.event.returnValue = false;
            }
        }
    }
});
