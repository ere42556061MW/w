// script.js - Bot Manager Frontend
// Smooth page transition
document.addEventListener('DOMContentLoaded', function() {
    document.body.style.opacity = '0';
    setTimeout(function() {
        document.body.style.transition = 'opacity 0.3s ease';
        document.body.style.opacity = '1';
    }, 10);
});

$(document).ready(function() {
    // Fallback data
    const fallbackBots = [
        { id: 'bot_sample_1', name: 'Bot Main', status: 'online' },
        { id: 'bot_sample_2', name: 'Bot Backup', status: 'online' },
        { id: 'bot_sample_3', name: 'Bot Test', status: 'offline' }
    ];

    const fallbackGroups = [
        { id: 'group_sample_1', name: 'Nhóm Học Tập', members: 45, online: 12 },
        { id: 'group_sample_2', name: 'Nhóm Công Việc', members: 23, online: 8 },
        { id: 'group_sample_3', name: 'Gia Đình', members: 8, online: 5 },
        { id: 'group_sample_4', name: 'Nhóm Game', members: 67, online: 23 },
        { id: 'group_sample_5', name: 'Dự Án X', members: 15, online: 7 }
    ];

    const fallbackFriends = [
        { id: 'friend_sample_1', name: 'Nguyễn Văn A', status: 'Online' },
        { id: 'friend_sample_2', name: 'Trần Thị B', status: 'Offline' },
        { id: 'friend_sample_3', name: 'Lê Văn C', status: 'Online' },
        { id: 'friend_sample_4', name: 'Phạm Thị D', status: 'Away' },
        { id: 'friend_sample_5', name: 'Hoàng Văn E', status: 'Online' }
    ];

    let bots = [...fallbackBots];
    let groups = [...fallbackGroups];
    let friends = [...fallbackFriends];
    let activeBotId = bots[0]?.id || null;

    let selectedTarget = null;
    let selectedType = null;
    let logCount = 0;
    let selectedRentalDays = 15;
    let selectedRentalPrice = 90000;
    let selectedPaymentMethod = 'momo';
    let paymentTimer = null;
    let commandsData = {};
    let isThreadMode = false;
    let generalLogs = [];
    let isLoggedIn = false;
    let currentUser = null;

    const commands = [
        { id: 1, name: 'AI Chat', icon: '🤖', desc: 'Trò chuyện với AI thông minh', price: 50000 },
        { id: 2, name: 'Music', icon: '🎵', desc: 'Phát nhạc từ YouTube', price: 30000 },
        { id: 3, name: 'Image Gen', icon: '🎨', desc: 'Tạo ảnh từ văn bản', price: 70000 },
        { id: 4, name: 'Translate', icon: '🌐', desc: 'Dịch ngôn ngữ tự động', price: 20000 },
        { id: 5, name: 'Weather', icon: '🌤️', desc: 'Xem thời tiết realtime', price: 15000 },
        { id: 6, name: 'Wiki Search', icon: '📚', desc: 'Tra cứu Wikipedia', price: 25000 },
        { id: 7, name: 'TikTok Down', icon: '📱', desc: 'Tải video TikTok', price: 40000 },
        { id: 8, name: 'Game Mini', icon: '🎮', desc: 'Các mini game vui nhộn', price: 35000 }
    ];

    commands.forEach(cmd => {
        commandsData[cmd.id] = { ...cmd, count: 0 };
    });

    // ==================== AUTHENTICATION ====================
    
    // Check login status from server
    function checkLoginFromServer() {
        $.ajax({
            url: '/api/auth/me',
            method: 'GET',
            success: function(response) {
                if (response.user) {
                    isLoggedIn = true;
                    currentUser = response.user;
                    showUserProfile(response.user);
                    localStorage.setItem('loggedInUser', JSON.stringify(response.user));
                }
            },
            error: function() {
                isLoggedIn = false;
                currentUser = null;
                showAuthButtons();
                localStorage.removeItem('loggedInUser');
            }
        });
    }

    function showUserProfile(user) {
        $('#auth-buttons').hide();
        $('#user-profile').show();
        $('#profile-name').text(user.username || user.fullname || 'User');
        $('#profile-avatar').text((user.username || user.fullname || 'U').charAt(0).toUpperCase());
    }

    function showAuthButtons() {
        $('#auth-buttons').show();
        $('#user-profile').hide();
    }

    function requireLogin() {
        if (!isLoggedIn) {
            alert('⚠️ Bạn cần đăng nhập để sử dụng tính năng này!');
            window.location.href = '/login/';
            return false;
        }
        return true;
    }

    // Login handler
    $('#login-btn').click(function() {
        const username = $('#login-username').val().trim();
        const password = $('#login-password').val().trim();

        if (!username || !password) {
            alert('⚠️ Vui lòng điền đầy đủ thông tin!');
            return;
        }

        const $btn = $(this);
        $btn.prop('disabled', true).text('⏳ Đang đăng nhập...');

        $.ajax({
            url: '/api/auth/login',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                username: username,
                password: password
            }),
            success: function(response) {
                if (response.success) {
                    isLoggedIn = true;
                    currentUser = response.user;
                    localStorage.setItem('loggedInUser', JSON.stringify(response.user));
                    showUserProfile(response.user);
                    alert('✅ Đăng nhập thành công!\n\nChào mừng ' + response.user.username + '!');
                    window.location.href = '/home/';
                }
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || 'Đăng nhập thất bại';
                alert('❌ ' + error);
            },
            complete: function() {
                $btn.prop('disabled', false).text('🔓 Đăng Nhập');
            }
        });
    });

    // Register handler
    $('#register-btn').click(function() {
        const fullname = $('#register-fullname').val().trim();
        const email = $('#register-email').val().trim();
        const username = $('#register-username').val().trim();
        const password = $('#register-password').val().trim();
        const confirm = $('#register-confirm').val().trim();
        const acceptTerms = $('#accept-terms').is(':checked');

        if (!fullname || !email || !username || !password || !confirm) {
            alert('⚠️ Vui lòng điền đầy đủ thông tin!');
            return;
        }

        if (password !== confirm) {
            alert('⚠️ Mật khẩu xác nhận không khớp!');
            return;
        }

        if (password.length < 8) {
            alert('⚠️ Mật khẩu phải có ít nhất 8 ký tự!');
            return;
        }

        if (!acceptTerms) {
            alert('⚠️ Vui lòng đồng ý với điều khoản dịch vụ!');
            return;
        }

        const $btn = $(this);
        $btn.prop('disabled', true).text('⏳ Đang đăng ký...');

        $.ajax({
            url: '/api/auth/register',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                username: username,
                email: email,
                password: password,
                fullname: fullname
            }),
            success: function(response) {
                if (response.success) {
                    alert('🎉 Đăng ký thành công!\n\nVui lòng đăng nhập để tiếp tục.');
                    window.location.href = '/login/';
                }
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || 'Đăng ký thất bại';
                alert('❌ ' + error);
            },
            complete: function() {
                $btn.prop('disabled', false).text('✨ Tạo Tài Khoản');
            }
        });
    });

    // Logout handler
    $('#logout-btn').click(function() {
        if (confirm('Bạn có chắc muốn đăng xuất?')) {
            $.ajax({
                url: '/api/auth/logout',
                method: 'POST',
                success: function() {
                    localStorage.removeItem('loggedInUser');
                    isLoggedIn = false;
                    currentUser = null;
                    showAuthButtons();
                    alert('👋 Đã đăng xuất thành công!');
                    window.location.href = '/login/';
                },
                error: function() {
                    alert('Có lỗi xảy ra khi đăng xuất');
                }
            });
        }
    });

    // Navigation auth handlers
    $('#nav-login-btn').click(function() {
        window.location.href = '/login/';
    });

    $('#nav-register-btn').click(function() {
        window.location.href = '/register/';
    });

    $('#goto-register').click(function(e) {
        e.preventDefault();
        window.location.href = '/register/';
    });

    $('#goto-login').click(function(e) {
        e.preventDefault();
        window.location.href = '/login/';
    });

    $('#login-google, #register-google').click(function() {
        alert('🌐 Đăng nhập với Google sẽ được cập nhật sớm!');
    });

    $('#login-facebook, #register-facebook').click(function() {
        alert('📘 Đăng nhập với Facebook sẽ được cập nhật sớm!');
    });

    // Forgot password handler
    $('#reset-password-btn').click(function() {
        const email = $('#forgot-email').val().trim();
        
        if (!email) {
            alert('⚠️ Vui lòng nhập email!');
            return;
        }

        const $btn = $(this);
        $btn.prop('disabled', true).text('⏳ Đang gửi...');

        $.ajax({
            url: '/api/auth/forgot-password',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ email: email }),
            success: function(response) {
                alert('✅ ' + response.message + '\n\nVui lòng kiểm tra email của bạn.');
                window.location.href = '/login/';
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || 'Không thể gửi email';
                alert('❌ ' + error);
            },
            complete: function() {
                $btn.prop('disabled', false).text('📧 Gửi Link Đặt Lại');
            }
        });
    });

    // ==================== PROFILE MANAGEMENT ====================
    
    // Profile dropdown items
    $('#profile-info').click(function() {
        $('#profile-dropdown').removeClass('show');
        window.location.href = '/profile/';
    });

    $('#profile-settings').click(function() {
        $('#profile-dropdown').removeClass('show');
        window.location.href = '/settings/';
    });

    // Load profile data from server
    function loadProfileData() {
        $.ajax({
            url: '/api/auth/me',
            method: 'GET',
            success: function(response) {
                if (response.user) {
                    const user = response.user;
                    $('#profile-display-name').text(user.fullname || user.username || 'User');
                    $('#profile-email').text(user.email || 'user@example.com');
                    $('#profile-fullname').val(user.fullname || '');
                    $('#profile-username').val(user.username || '');
                    $('#profile-email-input').val(user.email || '');
                    $('#profile-phone').val(user.phone || '');
                    $('#profile-birthday').val(user.birthday || '');
                    $('#profile-gender').val(user.gender || '');
                    $('#profile-avatar-large').text((user.username || 'U').charAt(0).toUpperCase());
                }
            }
        });
    }

    // Change avatar
    $('#change-avatar-btn').click(function() {
        alert('📷 Chức năng đổi avatar sẽ được cập nhật sớm!');
    });

    // Update profile
    $('#save-profile-btn').click(function() {
        const profileData = {
            fullname: $('#profile-fullname').val().trim(),
            email: $('#profile-email-input').val().trim(),
            phone: $('#profile-phone').val().trim(),
            birthday: $('#profile-birthday').val(),
            gender: $('#profile-gender').val()
        };

        const $btn = $(this);
        $btn.prop('disabled', true).text('⏳ Đang lưu...');

        $.ajax({
            url: '/api/auth/update-profile',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(profileData),
            success: function(response) {
                if (response.success) {
                    alert('✅ Đã lưu thông tin thành công!');
                    checkLoginFromServer();
                }
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || 'Không thể cập nhật thông tin';
                alert('❌ ' + error);
            },
            complete: function() {
                $btn.prop('disabled', false).text('💾 Lưu Thay Đổi');
            }
        });
    });

    // Change password
    $('#change-password-btn').click(function() {
        const oldPassword = prompt('Nhập mật khẩu hiện tại:');
        if (!oldPassword) return;

        const newPassword = prompt('Nhập mật khẩu mới (tối thiểu 8 ký tự):');
        if (!newPassword) return;

        if (newPassword.length < 8) {
            alert('⚠️ Mật khẩu phải có ít nhất 8 ký tự!');
            return;
        }

        const confirmPassword = prompt('Xác nhận mật khẩu mới:');
        if (newPassword !== confirmPassword) {
            alert('⚠️ Mật khẩu xác nhận không khớp!');
            return;
        }

        $.ajax({
            url: '/api/auth/change-password',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                old_password: oldPassword,
                new_password: newPassword
            }),
            success: function(response) {
                if (response.success) {
                    alert('✅ Đã đổi mật khẩu thành công!\n\nVui lòng đăng nhập lại.');
                    window.location.href = '/login/';
                }
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || 'Không thể đổi mật khẩu';
                alert('❌ ' + error);
            }
        });
    });

    // Export data
    $('#export-data-btn').click(function() {
        alert('📥 Dữ liệu của bạn đang được xuất...\n\nFile sẽ được tải xuống sau vài giây.');
    });

    // Delete account
    $('#delete-account-btn').click(function() {
        if (confirm('⚠️ BẠN CÓ CHẮC CHẮN MUỐN XÓA TÀI KHOẢN?\n\nHành động này KHÔNG THỂ HOÀN TÁC!')) {
            if (confirm('⚠️ XÁC NHẬN LẦN CUỐI!\n\nTất cả dữ liệu sẽ bị xóa vĩnh viễn!')) {
                const password = prompt('Nhập mật khẩu để xác nhận:');
                
                if (!password) return;

                $.ajax({
                    url: '/api/auth/delete-account',
                    method: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ password: password }),
                    success: function(response) {
                        if (response.success) {
                            localStorage.removeItem('loggedInUser');
                            alert('✅ Tài khoản đã được xóa!');
                            window.location.href = '/login/';
                        }
                    },
                    error: function(xhr) {
                        const error = xhr.responseJSON?.error || 'Không thể xóa tài khoản';
                        alert('❌ ' + error);
                    }
                });
            }
        }
    });

    // ==================== THEME & UI ====================
    
    // Theme mode cards
    $('.theme-mode-card').click(function() {
        $('.theme-mode-card').removeClass('active');
        $(this).addClass('active');
        const mode = $(this).data('mode');
        
        if (mode === 'light') {
            $('body').removeClass('dark');
            $('#theme-toggle-nav').text('🌙');
        } else if (mode === 'dark') {
            $('body').addClass('dark');
            $('#theme-toggle-nav').text('☀️');
        } else {
            const hour = new Date().getHours();
            if (hour >= 18 || hour < 6) {
                $('body').addClass('dark');
                $('#theme-toggle-nav').text('☀️');
            } else {
                $('body').removeClass('dark');
                $('#theme-toggle-nav').text('🌙');
            }
        }
    });

    $('.color-scheme').click(function() {
        $('.color-scheme').removeClass('active');
        $(this).addClass('active');
        const scheme = $(this).data('scheme');
        alert('🎨 Đã áp dụng bảng màu ' + $(this).find('.scheme-name').text());
    });

    $('.bg-option').click(function() {
        $('.bg-option').removeClass('active');
        $(this).addClass('active');
        const bg = $(this).data('bg');
        alert('🖼️ Đã áp dụng nền ' + $(this).find('.bg-name').text());
    });

    $('#save-theme-btn').click(function() {
        const theme = {
            mode: $('.theme-mode-card.active').data('mode'),
            colorScheme: $('.color-scheme.active').data('scheme'),
            font: $('#font-family').val(),
            fontSize: $('#font-size').val(),
            borderRadius: $('#border-radius').val(),
            animationSpeed: $('#animation-speed').val(),
            background: $('.bg-option.active').data('bg')
        };
        localStorage.setItem('userTheme', JSON.stringify(theme));
        alert('✅ Đã lưu theme thành công!');
    });

    $('#reset-theme-btn').click(function() {
        if (confirm('Bạn có chắc muốn đặt lại theme mặc định?')) {
            localStorage.removeItem('userTheme');
            location.reload();
        }
    });

    // Theme Toggle
    $('#theme-toggle-nav').click(function() {
        $('body').toggleClass('dark');
        const isDark = $('body').hasClass('dark');
        $(this).text(isDark ? '☀️' : '🌙');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });

    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        $('body').addClass('dark');
        $('#theme-toggle-nav').text('☀️');
    }

    // Navigation Menu Dropdown
    $('#nav-menu-btn').click(function(e) {
        e.stopPropagation();
        $('#nav-dropdown').toggleClass('show');
        $('#profile-dropdown').removeClass('show');
    });

    // User Profile Dropdown
    $('#user-profile-btn').click(function(e) {
        e.stopPropagation();
        $('#profile-dropdown').toggleClass('show');
        $('#nav-dropdown').removeClass('show');
    });

    // Close dropdowns when clicking outside
    $(document).click(function() {
        $('#nav-dropdown').removeClass('show');
        $('#profile-dropdown').removeClass('show');
    });

    // Prevent dropdown close when clicking inside
    $('.nav-dropdown, .profile-dropdown').click(function(e) {
        e.stopPropagation();
    });

    // ==================== DATA LOADING ====================
    
    async function loadDataFromAPI() {
        try {
            const botsResponse = await fetch('/api/bots');
            if (botsResponse.ok) {
                const botsJson = await botsResponse.json();
                if (Array.isArray(botsJson.bots) && botsJson.bots.length > 0) {
                    bots = botsJson.bots.map(bot => ({
                        id: bot.id,
                        name: bot.name || bot.id,
                        status: bot.status || 'unknown'
                    }));
                    activeBotId = bots[0].id;
                    
                    const dataResponse = await fetch(`/api/bot/${activeBotId}/data`);
                    if (dataResponse.ok) {
                        const dataJson = await dataResponse.json();
                        const data = dataJson.data || {};
                        
                        if (Array.isArray(data.groups) && data.groups.length) {
                            groups = data.groups.map((group, idx) => ({
                                id: group.group_id || group.id || idx,
                                name: group.name || 'Unknown Group',
                                members: group.members || 0,
                                online: group.online || 0
                            }));
                        }
                        
                        if (Array.isArray(data.friends) && data.friends.length) {
                            friends = data.friends.map((friend, idx) => ({
                                id: friend.user_id || friend.id || idx,
                                name: friend.name || friend.displayName || 'User',
                                status: friend.status || 'Online'
                            }));
                        }
                    }
                }
            }
        } catch (error) {
            console.warn('Không thể tải dữ liệu thật, dùng dữ liệu mẫu.', error);
            bots = [...fallbackBots];
            groups = [...fallbackGroups];
            friends = [...fallbackFriends];
        } finally {
            renderBotsManagement();
            renderGroups();
            renderFriends();
        }
    }

    // ==================== RENDER FUNCTIONS ====================
    
    function renderBotsManagement() {
        $('#bots-management-list').empty();
        bots.forEach(bot => {
            const statusClass = bot.status === 'online' ? 'online' : 'offline';
            const statusText = bot.status === 'online' ? '🟢 Online' : '🔴 Offline';
            const actionBtn = bot.status === 'online' 
                ? `<button class="bot-action-btn stop" data-bot-id="${bot.id}">⏸️ Dừng</button>`
                : `<button class="bot-action-btn start" data-bot-id="${bot.id}">▶️ Khởi động</button>`;
            
            const card = $(`
                <div class="bot-card">
                    <div class="bot-card-header">
                        <div class="bot-card-name">${bot.name}</div>
                        <div class="bot-card-status ${statusClass}">${statusText}</div>
                    </div>
                    <div class="bot-card-info">
                        <div class="bot-info-item"><span class="bot-info-label">ID:</span> ${bot.id}</div>
                        <div class="bot-info-item"><span class="bot-info-label">Uptime:</span> ${Math.floor(Math.random() * 48)}h</div>
                        <div class="bot-info-item"><span class="bot-info-label">Messages:</span> ${Math.floor(Math.random() * 1000)}</div>
                        <div class="bot-info-item"><span class="bot-info-label">Threads:</span> ${Math.floor(Math.random() * 50)}</div>
                    </div>
                    <div class="bot-card-actions">
                        ${actionBtn}
                        <button class="bot-action-btn delete" data-bot-id="${bot.id}">🗑️ Xóa</button>
                    </div>
                </div>
            `);
            $('#bots-management-list').append(card);
        });
    }

    function renderCommandsShop() {
        $('#commands-grid').empty();
        commands.forEach(cmd => {
            const isPurchased = commandsData[cmd.id].count > 0;
            const selectedClass = isPurchased ? 'selected' : '';
            const checkmark = isPurchased ? '<div class="selected-count">✓</div>' : '';
            
            const item = $(`
                <div class="command-item ${selectedClass}" data-cmd-id="${cmd.id}">
                    ${checkmark}
                    <div class="command-icon">${cmd.icon}</div>
                    <div class="command-name">${cmd.name}</div>
                    <div class="command-desc">${cmd.desc}</div>
                    <div class="command-price">${cmd.price.toLocaleString('vi-VN')}đ</div>
                </div>
            `);
            $('#commands-grid').append(item);
        });
        updateCommandsSummary();
    }

    function renderGroups() {
        $('#groups-list').empty();
        groups.forEach(group => {
            const item = $(`
                <div class="list-item" data-id="${group.id}" data-type="group">
                    <div class="avatar">${group.name.charAt(0)}</div>
                    <div class="item-info">
                        <div class="item-name">${group.name}</div>
                        <div class="item-status">${group.members} thành viên • ${group.online} online</div>
                    </div>
                </div>
            `);
            $('#groups-list').append(item);
        });
    }

    function renderFriends() {
        $('#friends-list').empty();
        friends.forEach(friend => {
            const statusColor = friend.status === 'Online' ? '#10b981' : 
                               friend.status === 'Away' ? '#f59e0b' : '#6c757d';
            const item = $(`
                <div class="list-item" data-id="${friend.id}" data-type="friend">
                    <div class="avatar">${friend.name.charAt(0)}</div>
                    <div class="item-info">
                        <div class="item-name">${friend.name}</div>
                        <div class="item-status" style="color: ${statusColor}">${friend.status}</div>
                    </div>
                </div>
            `);
            $('#friends-list').append(item);
        });
    }

    function updateCommandsSummary() {
        let total = 0;
        let count = 0;
        Object.values(commandsData).forEach(cmd => {
            if (cmd.count > 0) {
                total += cmd.price;
                count++;
            }
        });
        $('#commands-selected-count').text(count);
        $('#commands-total').text(`${total.toLocaleString('vi-VN')}đ`);
    }

    function updateRentalSummary() {
        $('#summary-days').text(`${selectedRentalDays} ngày`);
        $('#summary-price').text(`${selectedRentalPrice.toLocaleString('vi-VN')}đ`);
        $('#summary-total').text(`${selectedRentalPrice.toLocaleString('vi-VN')}đ`);
        
        const methodNames = { 'momo': 'MoMo', 'bank': 'Banking', 'card': 'Thẻ' };
        $('#summary-method').text(methodNames[selectedPaymentMethod]);
    }

    // ==================== LOG FUNCTIONS ====================
    
    window.addLog = function(type, sender, message, userData = {}) {
        if (isThreadMode) {
            const tempDiv = $('<div>').hide().appendTo('body');
            const logHTML = window.generateLogHTML(type, sender, message, userData);
            tempDiv.html(logHTML);
            generalLogs = (generalLogs || '') + tempDiv.html();
            tempDiv.remove();
            return;
        }
        
        logCount++;
        $('#log-count').text(logCount);
        const logHTML = window.generateLogHTML(type, sender, message, userData);
        $('#log-content').prepend(logHTML);
    };

    window.generateLogHTML = function(type, sender, message, userData = {}) {
        const time = new Date().toLocaleTimeString('vi-VN');
        const date = new Date().toLocaleDateString('vi-VN');
        
        if (type === 'message' && userData.userId) {
            return `
                <div class="log-entry">
                    <div class="log-box">
                        <div class="log-header">
                            <div>📋 Tin nhắn mới <span class="message-count">#${logCount}</span></div>
                            <span class="account-badge">${userData.account || 'Acc 1'}</span>
                        </div>
                        <div class="log-content-area">
                            <div class="log-row">
                                <span class="log-icon">💬</span>
                                <span class="log-label">Message:</span>
                                <span class="log-value">${message}</span>
                            </div>
                            <div class="log-row">
                                <span class="log-icon">👤</span>
                                <span class="log-label">User:</span>
                                <span class="log-value">${userData.userName || sender} (${userData.userId})</span>
                            </div>
                            <div class="log-row">
                                <span class="log-icon">💥</span>
                                <span class="log-label">Group:</span>
                                <span class="log-value">${userData.threadName || 'N/A'} (${userData.threadId || 'N/A'})</span>
                            </div>
                        </div>
                        <div class="log-footer">
                            <span>🆔 <strong>${userData.messageId || Math.floor(Math.random() * 10000000000000)}</strong></span>
                            <span>⚙️ <strong>${userData.threadType || 'ThreadType.GROUP'}</strong></span>
                            <span>⏰ <strong>${time} - ${date}</strong></span>
                        </div>
                    </div>
                </div>
            `;
        } else {
            const eventIcon = type === 'join' ? '🎉' : type === 'leave' ? '👋' : '⚙️';
            return `
                <div class="log-entry">
                    <div class="event-log">
                        <span class="event-icon">${eventIcon}</span>
                        <div class="event-content">
                            <span class="event-text">${message}</span>
                            <span class="event-time">${time} - ${date}</span>
                        </div>
                    </div>
                </div>
            `;
        }
    };

    function addThreadMessage(type, sender, message, time) {
        const bubble = $(`
            <div class="message-bubble ${type}">
                ${type === 'incoming' ? `<div class="message-sender">${sender}</div>` : ''}
                <div class="message-content">
                    <div class="message-text">${message}</div>
                    <div class="message-time">${time}</div>
                </div>
            </div>
        `);
        $('#log-content').append(bubble);
        
        const logContent = $('#log-content')[0];
        setTimeout(() => {
            logContent.scrollTop = logContent.scrollHeight;
        }, 100);
    }

    function saveGeneralLogs() {
        if (!isThreadMode) {
            generalLogs = $('#log-content').html();
        }
    }

    function restoreGeneralLogs() {
        $('#log-content').empty();
        if (generalLogs) {
            $('#log-content').html(generalLogs);
        }
    }

    function startPaymentTimer() {
        let timeLeft = 900;
        if (paymentTimer) clearInterval(paymentTimer);
        
        paymentTimer = setInterval(() => {
            timeLeft--;
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            $('#payment-timer').text(`⏰ Thời gian còn lại: ${minutes}:${seconds.toString().padStart(2, '0')}`);
            
            if (timeLeft <= 0) {
                clearInterval(paymentTimer);
                alert('⏰ Hết thời gian thanh toán!');
                window.location.href = '/rental/';
            }
        }, 1000);
    }

    // ==================== EVENT HANDLERS ====================
    
    // Tabs
    $('.tab').click(function() {
        $('.tab').removeClass('active');
        $(this).addClass('active');
        const tab = $(this).data('tab');
        $('.list-content').hide();
        $(`#${tab}-list`).show();
    });

    // List items
    $(document).on('click', '.list-item', function() {
        if ($(this).hasClass('active')) {
            $(this).removeClass('active');
            selectedTarget = null;
            selectedType = null;
            isThreadMode = false;
            $('#log-content').removeClass('thread-mode');
            restoreGeneralLogs();
            $('#message-composer').removeClass('show');
            return;
        }
        
        $('.list-item').removeClass('active');
        $(this).addClass('active');
        selectedTarget = $(this).data('id');
        selectedType = $(this).data('type');
        const name = $(this).find('.item-name').text();
        
        saveGeneralLogs();
        isThreadMode = true;
        $('#log-content').addClass('thread-mode');
        $('#log-content').empty();
        $('#message-composer').addClass('show');
        $('#composer-textarea').attr('placeholder', `Nhập tin nhắn gửi đến ${name}...`);
        
        addThreadMessage('incoming', 'Nguyễn Văn A', 'Chào mọi người!', '10:30');
        addThreadMessage('incoming', 'Trần Thị B', 'Hello', '10:32');
        addThreadMessage('outgoing', 'Bot', 'Xin chào! Tôi có thể giúp gì cho bạn?', '10:33');
    });

    // Composer send
    $('#composer-send-btn').click(function() {
        const message = $('#composer-textarea').val().trim();
        if (!selectedTarget) {
            alert('Vui lòng chọn thread trước!');
            return;
        }
        if (!message) {
            alert('Vui lòng nhập tin nhắn!');
            return;
        }
        
        const now = new Date();
        const time = now.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
        addThreadMessage('outgoing', 'Bot', message, time);
        $('#composer-textarea').val('');
        
        setTimeout(() => {
            addThreadMessage('incoming', 'User', 'Đã nhận tin nhắn!', time);
        }, 1000);
    });

    // Composer send all
    $('#composer-send-all').click(function() {
        const message = $('#composer-textarea').val().trim();
        if (!message) {
            alert('Vui lòng nhập tin nhắn!');
            return;
        }
        if (isThreadMode) {
            alert('Không thể gửi All khi đang trong thread. Vui lòng hủy chọn thread!');
            return;
        }
        
        const activeTab = $('.tab.active').data('tab');
        const count = activeTab === 'groups' ? groups.length : friends.length;
        addLog('event', '📢 BOT', `Đã gửi tin nhắn đến tất cả ${count} ${activeTab === 'groups' ? 'nhóm' : 'bạn bè'}: ${message}`);
        $('#composer-textarea').val('');
    });

    // Composer run command
    $('#composer-run-cmd').click(function() {
        const message = $('#composer-textarea').val().trim();
        if (!message) {
            alert('Vui lòng nhập lệnh!');
            return;
        }
        
        if (isThreadMode) {
            const now = new Date();
            const time = now.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
            addThreadMessage('outgoing', 'Bot', `⚡ ${message}`, time);
            $('#composer-textarea').val('');
            setTimeout(() => {
                addThreadMessage('incoming', 'System', `✅ Lệnh "${message}" đã được thực thi`, time);
            }, 1000);
        } else {
            addLog('event', '⚡ SYSTEM', `Đang chạy lệnh: ${message}`);
            $('#composer-textarea').val('');
            setTimeout(() => {
                addLog('event', '✅ SYSTEM', `Lệnh "${message}" đã được thực thi thành công`);
            }, 1000);
        }
    });

    // ==================== BOT MANAGEMENT ====================
    
    $(document).on('click', '.bot-action-btn.start', function() {
        const botId = $(this).data('bot-id');
        const bot = bots.find(b => b.id === botId);
        if (bot) {
            bot.status = 'online';
            renderBotsManagement();
            addLog('event', '🤖 SYSTEM', `Bot "${bot.name}" đã được khởi động`);
        }
    });

    $(document).on('click', '.bot-action-btn.stop', function() {
        const botId = $(this).data('bot-id');
        const bot = bots.find(b => b.id === botId);
        if (bot) {
            bot.status = 'offline';
            renderBotsManagement();
            addLog('event', '🤖 SYSTEM', `Bot "${bot.name}" đã bị dừng`);
        }
    });

    $(document).on('click', '.bot-action-btn.delete', function() {
        const botId = $(this).data('bot-id');
        const bot = bots.find(b => b.id === botId);
        if (bot && confirm(`Bạn có chắc muốn xóa bot "${bot.name}"?`)) {
            const index = bots.findIndex(b => b.id === botId);
            bots.splice(index, 1);
            renderBotsManagement();
            addLog('event', '🤖 SYSTEM', `Bot "${bot.name}" đã bị xóa`);
        }
    });

    $('#start-all-bots').click(function() {
        bots.forEach(bot => bot.status = 'online');
        renderBotsManagement();
        addLog('event', '🤖 SYSTEM', 'Đã khởi động tất cả bot');
    });

    $('#stop-all-bots').click(function() {
        bots.forEach(bot => bot.status = 'offline');
        renderBotsManagement();
        addLog('event', '🤖 SYSTEM', 'Đã dừng tất cả bot');
    });

    $('#add-new-bot').click(function() {
        window.location.href = '/create/';
    });

    // ==================== CREATE BOT ====================
    
    $('.method-btn').click(function() {
        $('.method-btn').removeClass('active');
        $(this).addClass('active');
        const method = $(this).data('method');
        $('.create-form').removeClass('active');
        $(`#${method}-form`).addClass('active');
    });

    $('#create-bot-cookie').click(function() {
        const prefix = $('#bot-prefix').val().trim();
        const imei = $('#imei-input').val().trim();
        const cookie = $('#cookie-input').val().trim();

        if (!prefix || !imei || !cookie) {
            alert('Vui lòng điền đầy đủ thông tin!');
            return;
        }

        const botName = `Bot_${prefix}`;
        bots.push({ id: 'bot_' + Date.now(), name: botName, status: 'online' });
        alert(`Đã tạo bot "${botName}" thành công!`);
        $('#bot-prefix, #imei-input, #cookie-input').val('');
        window.location.href = '/manager/';
        addLog('event', '🤖 SYSTEM', `Bot mới: ${botName} [Prefix: ${prefix}]`);
    });

    $('#generate-qr').click(function() {
        const prefix = $('#bot-prefix-qr').val().trim();
        if (!prefix) {
            alert('Vui lòng nhập prefix!');
            return;
        }

        $(this).text('⏳ Đang tạo QR...');
        setTimeout(() => {
            $('.qr-code').html('📱');
            $(this).text('✅ QR đã tạo');
            setTimeout(() => {
                const botName = `Bot_${prefix}`;
                bots.push({ id: 'bot_' + Date.now(), name: botName, status: 'online' });
                alert(`Bot "${botName}" đã được tạo!`);
                $('#bot-prefix-qr').val('');
                window.location.href = '/manager/';
                addLog('event', '🤖 SYSTEM', `Bot qua QR: ${botName}`);
            }, 2000);
        }, 1500);
    });

    // ==================== RENTAL ====================
    
    $('.price-card').click(function() {
        $('.price-card').removeClass('active');
        $(this).addClass('active');
        selectedRentalDays = $(this).data('days');
        selectedRentalPrice = $(this).data('price');
        $('#custom-days').val('');
        updateRentalSummary();
    });

    $('#apply-custom-days').click(function() {
        const days = parseInt($('#custom-days').val());
        if (!days || days < 1) {
            alert('Vui lòng nhập số ngày hợp lệ!');
            return;
        }
        
        $('.price-card').removeClass('active');
        selectedRentalDays = days;
        let pricePerDay = days >= 90 ? 4500 : days >= 30 ? 5000 : days >= 15 ? 6000 : 7000;
        selectedRentalPrice = days * pricePerDay;
        updateRentalSummary();
        alert(`✅ Đã áp dụng: ${days} ngày - ${selectedRentalPrice.toLocaleString('vi-VN')}đ`);
    });

    $('.payment-method').click(function() {
        $('.payment-method').removeClass('active');
        $(this).addClass('active');
        selectedPaymentMethod = $(this).data('method');
        updateRentalSummary();
    });

    $('#rental-submit').click(function() {
        const prefix = $('#rental-prefix').val().trim();
        const email = $('#rental-email').val().trim();

        if (!prefix || !email) {
            alert('Vui lòng điền đầy đủ thông tin!');
            return;
        }

        $('#payment-prefix').text(prefix);
        $('#payment-days').text(`${selectedRentalDays} ngày`);
        $('#payment-method').text($('#summary-method').text());
        $('#payment-amount').text(`${selectedRentalPrice.toLocaleString('vi-VN')}đ`);
        
        window.location.href = '/payment/';
    });

    $('#payment-confirm').click(function() {
        if (paymentTimer) clearInterval(paymentTimer);
        $(this).text('⏳ Đang xác nhận...').prop('disabled', true);
        
        setTimeout(() => {
            alert('🎉 Thanh toán thành công!');
            window.location.href = '/home/';
            $(this).text('✅ Tôi Đã Thanh Toán').prop('disabled', false);
            $('#rental-prefix, #rental-email').val('');
        }, 2000);
    });

    $('#payment-cancel').click(function() {
        if (confirm('Bạn có chắc muốn hủy?')) {
            if (paymentTimer) clearInterval(paymentTimer);
            window.location.href = '/rental/';
        }
    });

    // ==================== COMMANDS ====================
    
    $(document).on('click', '.command-item', function() {
        const cmdId = $(this).data('cmd-id');
        if (commandsData[cmdId].count > 0) {
            alert('Bạn đã mua lệnh này rồi!');
            return;
        }
        commandsData[cmdId].count = 1;
        renderCommandsShop();
    });

    $('#buy-commands-btn').click(function() {
        const selectedItems = Object.values(commandsData).filter(cmd => cmd.count > 0);
        if (selectedItems.length === 0) {
            alert('Vui lòng chọn ít nhất 1 lệnh!');
            return;
        }
        
        let summary = 'Xác nhận mua:\n\n';
        selectedItems.forEach(cmd => {
            summary += `• ${cmd.name}: ${cmd.price.toLocaleString('vi-VN')}đ\n`;
        });
        summary += `\nTổng: ${$('#commands-total').text()}`;
        
        if (confirm(summary)) {
            alert('🎉 Đã mua thành công!');
        }
    });

    // ==================== SETTINGS ====================
    
    $('.toggle-switch').click(function() {
        $(this).toggleClass('active');
    });

    $(document).on('click', '.blacklist-remove', function() {
        $(this).closest('.blacklist-item').remove();
    });

    $('#add-blacklist-btn').click(function() {
        const userId = $('#blacklist-input').val().trim();
        if (!userId) {
            alert('Vui lòng nhập User ID!');
            return;
        }
        
        const item = $(`
            <div class="blacklist-item">
                <span>${userId}</span>
                <button class="blacklist-remove" data-id="${userId}">Xóa</button>
            </div>
        `);
        $('#blacklist-container').append(item);
        $('#blacklist-input').val('');
    });

    $('#save-settings-btn').click(function() {
        alert('✅ Đã lưu cài đặt thành công!');
    });

    $('#reset-settings-btn').click(function() {
        if (confirm('Bạn có chắc muốn đặt lại mặc định?')) {
            $('#setting-prefix').val('!');
            $('#setting-botname').val('Bot Zalo');
            $('#setting-language').val('vi');
            alert('✅ Đã đặt lại cài đặt mặc định!');
        }
    });

    // ==================== HISTORY ====================
    
    $('#export-history-btn').click(function() {
        alert('📥 Đã xuất lịch sử thành công!\n\nFile: history_export_' + new Date().toISOString().split('T')[0] + '.json');
    });

    $('#clear-history-btn').click(function() {
        if (confirm('⚠️ Bạn có chắc muốn xóa toàn bộ lịch sử?\n\nHành động này không thể hoàn tác!')) {
            alert('✅ Đã xóa lịch sử thành công!');
        }
    });

    // ==================== USERS MANAGEMENT ====================
    
    $('#user-search').on('input', function() {
        const searchTerm = $(this).val().toLowerCase();
        $('.user-item').each(function() {
            const name = $(this).find('.user-name').text().toLowerCase();
            const id = $(this).find('.user-id').text().toLowerCase();
            if (name.includes(searchTerm) || id.includes(searchTerm)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });

    $('#user-filter').change(function() {
        const filter = $(this).val();
        $('.user-item').each(function() {
            if (filter === 'all') {
                $(this).show();
            } else {
                const role = $(this).find('.user-role').hasClass(filter);
                if (role) {
                    $(this).show();
                } else {
                    $(this).hide();
                }
            }
        });
    });

    $('#add-user-btn').click(function() {
        const userId = prompt('Nhập User ID:');
        if (userId) {
            alert('✅ Đã thêm user thành công!\n\nUser ID: ' + userId);
        }
    });

    $(document).on('click', '.user-action-btn.edit', function() {
        const userId = $(this).data('user-id');
        const userName = $(this).closest('.user-item').find('.user-name').text();
        const newRole = prompt(`Đổi quyền cho ${userName}:\n\nadmin, mod, user`);
        if (newRole && ['admin', 'mod', 'user'].includes(newRole)) {
            alert(`✅ Đã đổi quyền ${userName} thành ${newRole}!`);
        }
    });

    $(document).on('click', '.user-action-btn.block', function() {
        const userId = $(this).data('user-id');
        const userName = $(this).closest('.user-item').find('.user-name').text();
        if (confirm(`⚠️ Bạn có chắc muốn chặn ${userName}?`)) {
            $(this).closest('.user-item').addClass('blocked');
            $(this).closest('.user-item').find('.user-role').removeClass('admin mod user').addClass('blocked');
            $(this).closest('.user-item').find('.role-badge').html('🚫 Blocked');
            alert(`✅ Đã chặn ${userName}!`);
        }
    });

    $(document).on('click', '.user-action-btn.unblock', function() {
        const userId = $(this).data('user-id');
        const userName = $(this).closest('.user-item').find('.user-name').text();
        if (confirm(`✅ Bạn có chắc muốn bỏ chặn ${userName}?`)) {
            $(this).closest('.user-item').removeClass('blocked');
            $(this).closest('.user-item').find('.user-role').removeClass('blocked').addClass('user');
            $(this).closest('.user-item').find('.role-badge').html('👤 User');
            alert(`✅ Đã bỏ chặn ${userName}!`);
        }
    });

    $(document).on('click', '.user-action-btn.delete', function() {
        const userId = $(this).data('user-id');
        const userName = $(this).closest('.user-item').find('.user-name').text();
        if (confirm(`⚠️ Bạn có chắc muốn xóa ${userName}?\n\nHành động này không thể hoàn tác!`)) {
            $(this).closest('.user-item').fadeOut(300, function() {
                $(this).remove();
            });
            alert(`✅ Đã xóa ${userName}!`);
        }
    });

    // ==================== INITIALIZE ====================
    
    // Check if on profile page
    if ($('#profile-page').length && $('#profile-page').hasClass('active')) {
        loadProfileData();
    }

    // Initialize
    renderBotsManagement();
    renderGroups();
    renderFriends();
    loadDataFromAPI();
    checkLoginFromServer();
    
    // Update rental summary on load
    if ($('#rental-page').length) {
        updateRentalSummary();
    }
    
    // Start payment timer if on payment page
    if ($('#payment-page').length && $('#payment-page').hasClass('active')) {
        startPaymentTimer();
    }
});