// script.js - Bot Manager Frontend
// Smooth page transition
document.addEventListener('DOMContentLoaded', function() {
    document.body.style.opacity = '0';
    setTimeout(function() {
        document.body.style.transition = 'opacity 0.3s ease';
        document.body.style.opacity = '1';
    }, 10);
    // Apply saved theme preference on initial load
    try {
        const savedTheme = localStorage.getItem('site-theme');
        if (savedTheme === 'dark') {
            document.documentElement.classList.add('dark');
            document.body.classList.add('dark');
        } else if (savedTheme === 'light') {
            document.documentElement.classList.remove('dark');
            document.body.classList.remove('dark');
        }
    } catch (e) {
        // ignore
    }
});

$(document).ready(function() {
    // ==================== API CONFIGURATION ====================
    const API_BASE_URL = window.location.origin; // hoáº·c 'http://localhost:5000'

    // Helper function cho API calls
    function apiCall(endpoint, options = {}) {
        return $.ajax({
            url: `${API_BASE_URL}${endpoint}`,
            method: options.method || 'GET',
            contentType: 'application/json',
            data: options.data ? JSON.stringify(options.data) : undefined,
            ...options
        });
    }

    // ==================== DATA & STATE ====================
    // Fallback data
    const fallbackBots = [
        { id: 'bot_sample_1', name: 'Bot Main', status: 'online' },
        { id: 'bot_sample_2', name: 'Bot Backup', status: 'online' },
        { id: 'bot_sample_3', name: 'Bot Test', status: 'offline' }
    ];

    const fallbackGroups = [
        { id: 'group_sample_1', name: 'NhÃ³m Há»c Táº­p', members: 45, online: 12 },
        { id: 'group_sample_2', name: 'NhÃ³m CÃ´ng Viá»‡c', members: 23, online: 8 },
        { id: 'group_sample_3', name: 'Gia ÄÃ¬nh', members: 8, online: 5 },
        { id: 'group_sample_4', name: 'NhÃ³m Game', members: 67, online: 23 },
        { id: 'group_sample_5', name: 'Dá»± Ãn X', members: 15, online: 7 }
    ];

    const fallbackFriends = [
        { id: 'friend_sample_1', name: 'Nguyá»…n VÄƒn A', status: 'Online' },
        { id: 'friend_sample_2', name: 'Tráº§n Thá»‹ B', status: 'Offline' },
        { id: 'friend_sample_3', name: 'LÃª VÄƒn C', status: 'Online' },
        { id: 'friend_sample_4', name: 'Pháº¡m Thá»‹ D', status: 'Away' },
        { id: 'friend_sample_5', name: 'HoÃ ng VÄƒn E', status: 'Online' }
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
        { id: 1, name: 'AI Chat', icon: 'ðŸ¤–', desc: 'TrÃ² chuyá»‡n vá»›i AI thÃ´ng minh', price: 50000 },
        { id: 2, name: 'Music', icon: 'ðŸŽµ', desc: 'PhÃ¡t nháº¡c tá»« YouTube', price: 30000 },
        { id: 3, name: 'Image Gen', icon: 'ðŸŽ¨', desc: 'Táº¡o áº£nh tá»« vÄƒn báº£n', price: 70000 },
        { id: 4, name: 'Translate', icon: 'ðŸŒ', desc: 'Dá»‹ch ngÃ´n ngá»¯ tá»± Ä‘á»™ng', price: 20000 },
        { id: 5, name: 'Weather', icon: 'ðŸŒ¤ï¸', desc: 'Xem thá»i tiáº¿t realtime', price: 15000 },
        { id: 6, name: 'Wiki Search', icon: 'ðŸ“š', desc: 'Tra cá»©u Wikipedia', price: 25000 },
        { id: 7, name: 'TikTok Down', icon: 'ðŸ“±', desc: 'Táº£i video TikTok', price: 40000 },
        { id: 8, name: 'Game Mini', icon: 'ðŸŽ®', desc: 'CÃ¡c mini game vui nhá»™n', price: 35000 }
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
                    // Reload bots after login confirmed
                    loadMyBotsFromAPI();
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
            alert('âš ï¸ Báº¡n cáº§n Ä‘Äƒng nháº­p Ä‘á»ƒ sá»­ dá»¥ng tÃ­nh nÄƒng nÃ y!');
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
            alert('âš ï¸ Vui lÃ²ng Ä‘iá»n Ä‘áº§y Ä‘á»§ thÃ´ng tin!');
            return;
        }

        const $btn = $(this);
        $btn.prop('disabled', true).text('â³ Äang Ä‘Äƒng nháº­p...');

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
                    alert('âœ… ÄÄƒng nháº­p thÃ nh cÃ´ng!\n\nChÃ o má»«ng ' + response.user.username + '!');
                    window.location.href = '/home/';
                }
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || 'ÄÄƒng nháº­p tháº¥t báº¡i';
                alert('âŒ ' + error);
            },
            complete: function() {
                $btn.prop('disabled', false).text('ðŸ”“ ÄÄƒng Nháº­p');
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
            alert('âš ï¸ Vui lÃ²ng Ä‘iá»n Ä‘áº§y Ä‘á»§ thÃ´ng tin!');
            return;
        }

        if (password !== confirm) {
            alert('âš ï¸ Máº­t kháº©u xÃ¡c nháº­n khÃ´ng khá»›p!');
            return;
        }

        if (password.length < 8) {
            alert('âš ï¸ Máº­t kháº©u pháº£i cÃ³ Ã­t nháº¥t 8 kÃ½ tá»±!');
            return;
        }

        if (!acceptTerms) {
            alert('âš ï¸ Vui lÃ²ng Ä‘á»“ng Ã½ vá»›i Ä‘iá»u khoáº£n dá»‹ch vá»¥!');
            return;
        }

        const $btn = $(this);
        $btn.prop('disabled', true).text('â³ Äang Ä‘Äƒng kÃ½...');

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
                    alert('ðŸŽ‰ ÄÄƒng kÃ½ thÃ nh cÃ´ng!\n\nVui lÃ²ng Ä‘Äƒng nháº­p Ä‘á»ƒ tiáº¿p tá»¥c.');
                    window.location.href = '/login/';
                }
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || 'ÄÄƒng kÃ½ tháº¥t báº¡i';
                alert('âŒ ' + error);
            },
            complete: function() {
                $btn.prop('disabled', false).text('âœ¨ Táº¡o TÃ i Khoáº£n');
            }
        });
    });

    // Logout handler
    $('#logout-btn').click(function() {
        if (confirm('Báº¡n cÃ³ cháº¯c muá»‘n Ä‘Äƒng xuáº¥t?')) {
            $.ajax({
                url: '/api/auth/logout',
                method: 'POST',
                success: function() {
                    localStorage.removeItem('loggedInUser');
                    isLoggedIn = false;
                    currentUser = null;
                    showAuthButtons();
                    alert('ðŸ‘‹ ÄÃ£ Ä‘Äƒng xuáº¥t thÃ nh cÃ´ng!');
                    window.location.href = '/login/';
                },
                error: function() {
                    alert('CÃ³ lá»—i xáº£y ra khi Ä‘Äƒng xuáº¥t');
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

    // Theme toggle from sidebar/button
    function setTheme(mode) {
        if (mode === 'dark') {
            document.documentElement.classList.add('dark');
            document.body.classList.add('dark');
            try { localStorage.setItem('site-theme', 'dark'); } catch(e){}
        } else {
            document.documentElement.classList.remove('dark');
            document.body.classList.remove('dark');
            try { localStorage.setItem('site-theme', 'light'); } catch(e){}
        }
        // Notify other parts of the page (and theme page) that theme changed
        try { window.dispatchEvent(new Event('site-theme-changed')); } catch(e) {}
    }

    // handle click on sidebar theme toggle
    $(document).on('click', '#theme-toggle-sidebar, #theme-toggle-nav', function(e){
        e.preventDefault();
        const isDark = document.body.classList.contains('dark') || document.documentElement.classList.contains('dark');
        setTheme(isDark ? 'light' : 'dark');
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
        alert('ðŸŒ ÄÄƒng nháº­p vá»›i Google sáº½ Ä‘Æ°á»£c cáº­p nháº­t sá»›m!');
    });

    $('#login-facebook, #register-facebook').click(function() {
        alert('ðŸ“˜ ÄÄƒng nháº­p vá»›i Facebook sáº½ Ä‘Æ°á»£c cáº­p nháº­t sá»›m!');
    });

    // Forgot password handler
    $('#reset-password-btn').click(function() {
        const email = $('#forgot-email').val().trim();
        
        if (!email) {
            alert('âš ï¸ Vui lÃ²ng nháº­p email!');
            return;
        }

        const $btn = $(this);
        $btn.prop('disabled', true).text('â³ Äang gá»­i...');

        $.ajax({
            url: '/api/auth/forgot-password',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ email: email }),
            success: function(response) {
                alert('âœ… ' + response.message + '\n\nVui lÃ²ng kiá»ƒm tra email cá»§a báº¡n.');
                window.location.href = '/login/';
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || 'KhÃ´ng thá»ƒ gá»­i email';
                alert('âŒ ' + error);
            },
            complete: function() {
                $btn.prop('disabled', false).text('ðŸ“§ Gá»­i Link Äáº·t Láº¡i');
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
        alert('ðŸ“· Chá»©c nÄƒng Ä‘á»•i avatar sáº½ Ä‘Æ°á»£c cáº­p nháº­t sá»›m!');
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
        $btn.prop('disabled', true).text('â³ Äang lÆ°u...');

        $.ajax({
            url: '/api/auth/update-profile',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(profileData),
            success: function(response) {
                if (response.success) {
                    alert('âœ… ÄÃ£ lÆ°u thÃ´ng tin thÃ nh cÃ´ng!');
                    checkLoginFromServer();
                }
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || 'KhÃ´ng thá»ƒ cáº­p nháº­t thÃ´ng tin';
                alert('âŒ ' + error);
            },
            complete: function() {
                $btn.prop('disabled', false).text('ðŸ’¾ LÆ°u Thay Äá»•i');
            }
        });
    });

    // Change password
    $('#change-password-btn').click(function() {
        const oldPassword = prompt('Nháº­p máº­t kháº©u hiá»‡n táº¡i:');
        if (!oldPassword) return;

        const newPassword = prompt('Nháº­p máº­t kháº©u má»›i (tá»‘i thiá»ƒu 8 kÃ½ tá»±):');
        if (!newPassword) return;

        if (newPassword.length < 8) {
            alert('âš ï¸ Máº­t kháº©u pháº£i cÃ³ Ã­t nháº¥t 8 kÃ½ tá»±!');
            return;
        }

        const confirmPassword = prompt('XÃ¡c nháº­n máº­t kháº©u má»›i:');
        if (newPassword !== confirmPassword) {
            alert('âš ï¸ Máº­t kháº©u xÃ¡c nháº­n khÃ´ng khá»›p!');
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
                    alert('âœ… ÄÃ£ Ä‘á»•i máº­t kháº©u thÃ nh cÃ´ng!\n\nVui lÃ²ng Ä‘Äƒng nháº­p láº¡i.');
                    window.location.href = '/login/';
                }
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || 'KhÃ´ng thá»ƒ Ä‘á»•i máº­t kháº©u';
                alert('âŒ ' + error);
            }
        });
    });

    // Export data
    $('#export-data-btn').click(function() {
        alert('ðŸ“¥ Dá»¯ liá»‡u cá»§a báº¡n Ä‘ang Ä‘Æ°á»£c xuáº¥t...\n\nFile sáº½ Ä‘Æ°á»£c táº£i xuá»‘ng sau vÃ i giÃ¢y.');
    });

    // Delete account
    $('#delete-account-btn').click(function() {
        if (confirm('âš ï¸ Báº N CÃ“ CHáº®C CHáº®N MUá»N XÃ“A TÃ€I KHOáº¢N?\n\nHÃ nh Ä‘á»™ng nÃ y KHÃ”NG THá»‚ HOÃ€N TÃC!')) {
            if (confirm('âš ï¸ XÃC NHáº¬N Láº¦N CUá»I!\n\nTáº¥t cáº£ dá»¯ liá»‡u sáº½ bá»‹ xÃ³a vÄ©nh viá»…n!')) {
                const password = prompt('Nháº­p máº­t kháº©u Ä‘á»ƒ xÃ¡c nháº­n:');
                
                if (!password) return;

                $.ajax({
                    url: '/api/auth/delete-account',
                    method: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ password: password }),
                    success: function(response) {
                        if (response.success) {
                            localStorage.removeItem('loggedInUser');
                            alert('âœ… TÃ i khoáº£n Ä‘Ã£ Ä‘Æ°á»£c xÃ³a!');
                            window.location.href = '/login/';
                        }
                    },
                    error: function(xhr) {
                        const error = xhr.responseJSON?.error || 'KhÃ´ng thá»ƒ xÃ³a tÃ i khoáº£n';
                        alert('âŒ ' + error);
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
            $('#theme-toggle-nav').text('ðŸŒ™');
        } else if (mode === 'dark') {
            $('body').addClass('dark');
            $('#theme-toggle-nav').text('â˜€ï¸');
        } else {
            const hour = new Date().getHours();
            if (hour >= 18 || hour < 6) {
                $('body').addClass('dark');
                $('#theme-toggle-nav').text('â˜€ï¸');
            } else {
                $('body').removeClass('dark');
                $('#theme-toggle-nav').text('ðŸŒ™');
            }
        }
    });

    $('.color-scheme').click(function() {
        $('.color-scheme').removeClass('active');
        $(this).addClass('active');
        const scheme = $(this).data('scheme');
        alert('ðŸŽ¨ ÄÃ£ Ã¡p dá»¥ng báº£ng mÃ u ' + $(this).find('.scheme-name').text());
    });

    $('.bg-option').click(function() {
        $('.bg-option').removeClass('active');
        $(this).addClass('active');
        const bg = $(this).data('bg');
        alert('ðŸ–¼ï¸ ÄÃ£ Ã¡p dá»¥ng ná»n ' + $(this).find('.bg-name').text());
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
        alert('âœ… ÄÃ£ lÆ°u theme thÃ nh cÃ´ng!');
    });

    $('#reset-theme-btn').click(function() {
        if (confirm('Báº¡n cÃ³ cháº¯c muá»‘n Ä‘áº·t láº¡i theme máº·c Ä‘á»‹nh?')) {
            localStorage.removeItem('userTheme');
            location.reload();
        }
    });

    // Theme Toggle
    $('#theme-toggle-nav').click(function() {
        $('body').toggleClass('dark');
        const isDark = $('body').hasClass('dark');
        $(this).text(isDark ? 'â˜€ï¸' : 'ðŸŒ™');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });

    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        $('body').addClass('dark');
        $('#theme-toggle-nav').text('â˜€ï¸');
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
    
    // Load user's bots from server
    async function loadMyBotsFromAPI() {
        if (!isLoggedIn) {
            bots = [...fallbackBots];
            renderBotsManagement();
            return;
        }
        try {
            const response = await apiCall('/api/my-bots');
            if (response.bots && response.bots.length > 0) {
                bots = response.bots.map(bot => ({
                    id: bot.id,
                    name: bot.name,
                    status: bot.status || 'offline',
                    token: bot.token,
                    created_at: bot.created_at
                }));
                activeBotId = bots[0]?.id;
                
                // Load data for first bot
                if (activeBotId) {
                    const botData = await apiCall(`/api/my-bots/${activeBotId}/data`);
                    if (botData.data) {
                        groups = botData.data.groups || fallbackGroups;
                        friends = botData.data.friends || fallbackFriends;
                    }
                }
            }
        } catch (error) {
            console.warn('KhÃ´ng thá»ƒ táº£i bots, dÃ¹ng dá»¯ liá»‡u máº«u', error);
            bots = [...fallbackBots];
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
            const statusText = bot.status === 'online' ? 'ðŸŸ¢ Online' : 'ðŸ”´ Offline';
            const actionBtn = bot.status === 'online' 
                ? `<button class="bot-action-btn stop" data-bot-id="${bot.id}">â¸ï¸ Dá»«ng</button>`
                : `<button class="bot-action-btn start" data-bot-id="${bot.id}">â–¶ï¸ Khá»Ÿi Ä‘á»™ng</button>`;
            
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
                        <button class="bot-action-btn delete" data-bot-id="${bot.id}">ðŸ—‘ï¸ XÃ³a</button>
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
            const checkmark = isPurchased ? '<div class="selected-count">âœ“</div>' : '';
            
            const item = $(`
                <div class="command-item ${selectedClass}" data-cmd-id="${cmd.id}">
                    ${checkmark}
                    <div class="command-icon">${cmd.icon}</div>
                    <div class="command-name">${cmd.name}</div>
                    <div class="command-desc">${cmd.desc}</div>
                    <div class="command-price">${cmd.price.toLocaleString('vi-VN')}Ä‘</div>
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
                        <div class="item-status">${group.members} thÃ nh viÃªn â€¢ ${group.online} online</div>
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
        $('#commands-total').text(`${total.toLocaleString('vi-VN')}Ä‘`);
    }

    function updateRentalSummary() {
        $('#summary-days').text(`${selectedRentalDays} ngÃ y`);
        $('#summary-price').text(`${selectedRentalPrice.toLocaleString('vi-VN')}Ä‘`);
        $('#summary-total').text(`${selectedRentalPrice.toLocaleString('vi-VN')}Ä‘`);
        
        const methodNames = { 'momo': 'MoMo', 'bank': 'Banking', 'card': 'Tháº»' };
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
                            <div>ðŸ“‹ Tin nháº¯n má»›i <span class="message-count">#${logCount}</span></div>
                            <span class="account-badge">${userData.account || 'Acc 1'}</span>
                        </div>
                        <div class="log-content-area">
                            <div class="log-row">
                                <span class="log-icon">ðŸ’¬</span>
                                <span class="log-label">Message:</span>
                                <span class="log-value">${message}</span>
                            </div>
                            <div class="log-row">
                                <span class="log-icon">ðŸ‘¤</span>
                                <span class="log-label">User:</span>
                                <span class="log-value">${userData.userName || sender} (${userData.userId})</span>
                            </div>
                            <div class="log-row">
                                <span class="log-icon">ðŸ’¥</span>
                                <span class="log-label">Group:</span>
                                <span class="log-value">${userData.threadName || 'N/A'} (${userData.threadId || 'N/A'})</span>
                            </div>
                        </div>
                        <div class="log-footer">
                            <span>ðŸ†” <strong>${userData.messageId || Math.floor(Math.random() * 10000000000000)}</strong></span>
                            <span>âš™ï¸ <strong>${userData.threadType || 'ThreadType.GROUP'}</strong></span>
                            <span>â° <strong>${time} - ${date}</strong></span>
                        </div>
                    </div>
                </div>
            `;
        } else {
            const eventIcon = type === 'join' ? 'ðŸŽ‰' : type === 'leave' ? 'ðŸ‘‹' : 'âš™ï¸';
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
            $('#payment-timer').text(`â° Thá»i gian cÃ²n láº¡i: ${minutes}:${seconds.toString().padStart(2, '0')}`);
            
            if (timeLeft <= 0) {
                clearInterval(paymentTimer);
                alert('â° Háº¿t thá»i gian thanh toÃ¡n!');
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
        $('#composer-textarea').attr('placeholder', `Nháº­p tin nháº¯n gá»­i Ä‘áº¿n ${name}...`);
        
        addThreadMessage('incoming', 'Nguyá»…n VÄƒn A', 'ChÃ o má»i ngÆ°á»i!', '10:30');
        addThreadMessage('incoming', 'Tráº§n Thá»‹ B', 'Hello', '10:32');
        addThreadMessage('outgoing', 'Bot', 'Xin chÃ o! TÃ´i cÃ³ thá»ƒ giÃºp gÃ¬ cho báº¡n?', '10:33');
    });

    // Composer send
    $('#composer-send-btn').click(function() {
        const message = $('#composer-textarea').val().trim();
        if (!selectedTarget) {
            alert('Vui lÃ²ng chá»n thread trÆ°á»›c!');
            return;
        }
        if (!message) {
            alert('Vui lÃ²ng nháº­p tin nháº¯n!');
            return;
        }
        
        const now = new Date();
        const time = now.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
        addThreadMessage('outgoing', 'Bot', message, time);
        $('#composer-textarea').val('');
        
        setTimeout(() => {
            addThreadMessage('incoming', 'User', 'ÄÃ£ nháº­n tin nháº¯n!', time);
        }, 1000);
    });

    // Composer send all
    $('#composer-send-all').click(function() {
        const message = $('#composer-textarea').val().trim();
        if (!message) {
            alert('Vui lÃ²ng nháº­p tin nháº¯n!');
            return;
        }
        if (isThreadMode) {
            alert('KhÃ´ng thá»ƒ gá»­i All khi Ä‘ang trong thread. Vui lÃ²ng há»§y chá»n thread!');
            return;
        }
        
        const activeTab = $('.tab.active').data('tab');
        const count = activeTab === 'groups' ? groups.length : friends.length;
        addLog('event', 'ðŸ“¢ BOT', `ÄÃ£ gá»­i tin nháº¯n Ä‘áº¿n táº¥t cáº£ ${count} ${activeTab === 'groups' ? 'nhÃ³m' : 'báº¡n bÃ¨'}: ${message}`);
        $('#composer-textarea').val('');
    });

    // Composer run command
    $('#composer-run-cmd').click(function() {
        const message = $('#composer-textarea').val().trim();
        if (!message) {
            alert('Vui lÃ²ng nháº­p lá»‡nh!');
            return;
        }
        
        if (isThreadMode) {
            const now = new Date();
            const time = now.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
            addThreadMessage('outgoing', 'Bot', `âš¡ ${message}`, time);
            $('#composer-textarea').val('');
            setTimeout(() => {
                addThreadMessage('incoming', 'System', `âœ… Lá»‡nh "${message}" Ä‘Ã£ Ä‘Æ°á»£c thá»±c thi`, time);
            }, 1000);
        } else {
            addLog('event', 'âš¡ SYSTEM', `Äang cháº¡y lá»‡nh: ${message}`);
            $('#composer-textarea').val('');
            setTimeout(() => {
                addLog('event', 'âœ… SYSTEM', `Lá»‡nh "${message}" Ä‘Ã£ Ä‘Æ°á»£c thá»±c thi thÃ nh cÃ´ng`);
            }, 1000);
        }
    });

    // ==================== BOT MANAGEMENT ====================
    
    $(document).on('click', '.bot-action-btn.start, .bot-action-btn.stop', function() {
        const botId = $(this).data('bot-id');
        const bot = bots.find(b => b.id === botId);
        const isStart = $(this).hasClass('start');
        
        if (!bot) return;
        // Update local status immediately for UX
        bot.status = isStart ? 'online' : 'offline';
        renderBotsManagement();
        
        // Update server (optional - náº¿u bot tá»± update status thÃ¬ khÃ´ng cáº§n)
        addLog('event', 'ðŸ¤– SYSTEM', `Bot "${bot.name}" ${isStart ? 'Ä‘Ã£ khá»Ÿi Ä‘á»™ng' : 'Ä‘Ã£ dá»«ng'}`);
    });

    $(document).on('click', '.bot-action-btn.delete', function() {
        if (!requireLogin()) return;
        
        const botId = $(this).data('bot-id');
        const bot = bots.find(b => b.id === botId);
        
        if (!bot) return;
        
        if (!confirm(`âš ï¸ XÃ³a bot "${bot.name}"?\n\nHÃ nh Ä‘á»™ng khÃ´ng thá»ƒ hoÃ n tÃ¡c!`)) return;
        const $btn = $(this);
        $btn.prop('disabled', true).text('â³');
        apiCall(`/api/my-bots/${botId}`, {
            method: 'DELETE'
        }).done(function() {
            bots = bots.filter(b => b.id !== botId);
            renderBotsManagement();
            addLog('event', 'ðŸ—‘ï¸ SYSTEM', `Bot "${bot.name}" Ä‘Ã£ bá»‹ xÃ³a`);
        }).fail(function(xhr) {
            alert('âŒ ' + (xhr.responseJSON?.error || 'KhÃ´ng thá»ƒ xÃ³a bot'));
            $btn.prop('disabled', false).text('ðŸ—‘ï¸ XÃ³a');
        });
    });

    $(document).on('dblclick', '.bot-card-name', function() {
        if (!requireLogin()) return;
        
        const $card = $(this).closest('.bot-card');
        const botId = $card.find('.bot-action-btn').first().data('bot-id');
        const bot = bots.find(b => b.id === botId);
        
        if (!bot) return;
        
        const newName = prompt('Nháº­p tÃªn má»›i:', bot.name);
        if (!newName || newName === bot.name) return;
        apiCall(`/api/my-bots/${botId}`, {
            method: 'PUT',
            data: { name: newName }
        }).done(function() {
            bot.name = newName;
            renderBotsManagement();
            alert('âœ… ÄÃ£ Ä‘á»•i tÃªn thÃ nh cÃ´ng!');
        }).fail(function(xhr) {
            alert('âŒ ' + (xhr.responseJSON?.error || 'KhÃ´ng thá»ƒ Ä‘á»•i tÃªn'));
        });
    });

    $(document).on('click', '.bot-card-info', function() {
        if (!requireLogin()) return;
        
        const $card = $(this).closest('.bot-card');
        const botId = $card.find('.bot-action-btn').first().data('bot-id');
        
        apiCall(`/api/my-bots/${botId}/token`).done(function(response) {
            const token = response.token;
            if (confirm('ðŸ“‹ Bot Token:\n\n' + token + '\n\nCopy vÃ o clipboard?')) {
                navigator.clipboard.writeText(token);
                alert('âœ… ÄÃ£ copy token!');
            }
        }).fail(function(xhr) {
            alert('âŒ ' + (xhr.responseJSON?.error || 'KhÃ´ng thá»ƒ láº¥y token'));
        });
    });

    $('#start-all-bots').click(function() {
        bots.forEach(bot => bot.status = 'online');
        renderBotsManagement();
        addLog('event', 'ðŸ¤– SYSTEM', 'ÄÃ£ khá»Ÿi Ä‘á»™ng táº¥t cáº£ bot');
    });

    $('#stop-all-bots').click(function() {
        bots.forEach(bot => bot.status = 'offline');
        renderBotsManagement();
        addLog('event', 'ðŸ¤– SYSTEM', 'ÄÃ£ dá»«ng táº¥t cáº£ bot');
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
        if (!requireLogin()) return;
        
        const prefix = $('#bot-prefix').val().trim();
        const botName = prompt('Nháº­p tÃªn bot:', `Bot_${prefix}`);
        
        if (!botName) return;
        const $btn = $(this);
        $btn.prop('disabled', true).text('â³ Äang táº¡o...');
        apiCall('/api/my-bots', {
            method: 'POST',
            data: {
                name: botName,
                metadata: { prefix: prefix }
            }
        }).done(function(response) {
            if (response.success) {
                alert(`âœ… Táº¡o bot thÃ nh cÃ´ng!\n\nBot ID: ${response.bot_id}\nToken: ${response.token}\n\nâš ï¸ LÆ°u token nÃ y!`);
                
                // Add to local list
                bots.push({
                    id: response.bot_id,
                    name: botName,
                    status: 'offline',
                    token: response.token
                });
                
                renderBotsManagement();
                $('#bot-prefix, #imei-input, #cookie-input').val('');
            }
        }).fail(function(xhr) {
            alert('âŒ ' + (xhr.responseJSON?.error || 'KhÃ´ng thá»ƒ táº¡o bot'));
        }).always(function() {
            $btn.prop('disabled', false).text('ðŸš€ Táº¡o Bot');
        });
    });

    $('#generate-qr').click(function() {
        const prefix = $('#bot-prefix-qr').val().trim();
        if (!prefix) {
            alert('Vui lÃ²ng nháº­p prefix!');
            return;
        }

        $(this).text('â³ Äang táº¡o QR...');
        setTimeout(() => {
            $('.qr-code').html('ðŸ“±');
            $(this).text('âœ… QR Ä‘Ã£ táº¡o');
            setTimeout(() => {
                const botName = `Bot_${prefix}`;
                bots.push({ id: 'bot_' + Date.now(), name: botName, status: 'online' });
                alert(`Bot "${botName}" Ä‘Ã£ Ä‘Æ°á»£c táº¡o!`);
                $('#bot-prefix-qr').val('');
                window.location.href = '/manager/';
                addLog('event', 'ðŸ¤– SYSTEM', `Bot qua QR: ${botName}`);
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
            alert('Vui lÃ²ng nháº­p sá»‘ ngÃ y há»£p lá»‡!');
            return;
        }
        
        $('.price-card').removeClass('active');
        selectedRentalDays = days;
        let pricePerDay = days >= 90 ? 4500 : days >= 30 ? 5000 : days >= 15 ? 6000 : 7000;
        selectedRentalPrice = days * pricePerDay;
        updateRentalSummary();
        alert(`âœ… ÄÃ£ Ã¡p dá»¥ng: ${days} ngÃ y - ${selectedRentalPrice.toLocaleString('vi-VN')}Ä‘`);
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
            alert('Vui lÃ²ng Ä‘iá»n Ä‘áº§y Ä‘á»§ thÃ´ng tin!');
            return;
        }

        $('#payment-prefix').text(prefix);
        $('#payment-days').text(`${selectedRentalDays} ngÃ y`);
        $('#payment-method').text($('#summary-method').text());
        $('#payment-amount').text(`${selectedRentalPrice.toLocaleString('vi-VN')}Ä‘`);
        
        window.location.href = '/payment/';
    });

    $('#payment-confirm').click(function() {
        if (paymentTimer) clearInterval(paymentTimer);
        $(this).text('â³ Äang xÃ¡c nháº­n...').prop('disabled', true);
        
        setTimeout(() => {
            alert('ðŸŽ‰ Thanh toÃ¡n thÃ nh cÃ´ng!');
            window.location.href = '/home/';
            $(this).text('âœ… TÃ´i ÄÃ£ Thanh ToÃ¡n').prop('disabled', false);
            $('#rental-prefix, #rental-email').val('');
        }, 2000);
    });

    $('#payment-cancel').click(function() {
        if (confirm('Báº¡n cÃ³ cháº¯c muá»‘n há»§y?')) {
            if (paymentTimer) clearInterval(paymentTimer);
            window.location.href = '/rental/';
        }
    });

    // ==================== COMMANDS ====================
    
    $(document).on('click', '.command-item', function() {
        const cmdId = $(this).data('cmd-id');
        if (commandsData[cmdId].count > 0) {
            alert('Báº¡n Ä‘Ã£ mua lá»‡nh nÃ y rá»“i!');
            return;
        }
        commandsData[cmdId].count = 1;
        renderCommandsShop();
    });

    $('#buy-commands-btn').click(function() {
        const selectedItems = Object.values(commandsData).filter(cmd => cmd.count > 0);
        if (selectedItems.length === 0) {
            alert('Vui lÃ²ng chá»n Ã­t nháº¥t 1 lá»‡nh!');
            return;
        }
        
        let summary = 'XÃ¡c nháº­n mua:\n\n';
        selectedItems.forEach(cmd => {
            summary += `â€¢ ${cmd.name}: ${cmd.price.toLocaleString('vi-VN')}Ä‘\n`;
        });
        summary += `\nTá»•ng: ${$('#commands-total').text()}`;
        
        if (confirm(summary)) {
            alert('ðŸŽ‰ ÄÃ£ mua thÃ nh cÃ´ng!');
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
            alert('Vui lÃ²ng nháº­p User ID!');
            return;
        }
        
        const item = $(`
            <div class="blacklist-item">
                <span>${userId}</span>
                <button class="blacklist-remove" data-id="${userId}">XÃ³a</button>
            </div>
        `);
        $('#blacklist-container').append(item);
        $('#blacklist-input').val('');
    });

    $('#save-settings-btn').click(function() {
        alert('âœ… ÄÃ£ lÆ°u cÃ i Ä‘áº·t thÃ nh cÃ´ng!');
    });

    $('#reset-settings-btn').click(function() {
        if (confirm('Báº¡n cÃ³ cháº¯c muá»‘n Ä‘áº·t láº¡i máº·c Ä‘á»‹nh?')) {
            $('#setting-prefix').val('!');
            $('#setting-botname').val('Bot Zalo');
            $('#setting-language').val('vi');
            alert('âœ… ÄÃ£ Ä‘áº·t láº¡i cÃ i Ä‘áº·t máº·c Ä‘á»‹nh!');
        }
    });

    // ==================== HISTORY ====================
    
    $('#export-history-btn').click(function() {
        alert('ðŸ“¥ ÄÃ£ xuáº¥t lá»‹ch sá»­ thÃ nh cÃ´ng!\n\nFile: history_export_' + new Date().toISOString().split('T')[0] + '.json');
    });

    $('#clear-history-btn').click(function() {
        if (confirm('âš ï¸ Báº¡n cÃ³ cháº¯c muá»‘n xÃ³a toÃ n bá»™ lá»‹ch sá»­?\n\nHÃ nh Ä‘á»™ng nÃ y khÃ´ng thá»ƒ hoÃ n tÃ¡c!')) {
            alert('âœ… ÄÃ£ xÃ³a lá»‹ch sá»­ thÃ nh cÃ´ng!');
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
        const userId = prompt('Nháº­p User ID:');
        if (userId) {
            alert('âœ… ÄÃ£ thÃªm user thÃ nh cÃ´ng!\n\nUser ID: ' + userId);
        }
    });

    $(document).on('click', '.user-action-btn.edit', function() {
        const userId = $(this).data('user-id');
        const userName = $(this).closest('.user-item').find('.user-name').text();
        const newRole = prompt(`Äá»•i quyá»n cho ${userName}:\n\nadmin, mod, user`);
        if (newRole && ['admin', 'mod', 'user'].includes(newRole)) {
            alert(`âœ… ÄÃ£ Ä‘á»•i quyá»n ${userName} thÃ nh ${newRole}!`);
        }
    });

    $(document).on('click', '.user-action-btn.block', function() {
        const userId = $(this).data('user-id');
        const userName = $(this).closest('.user-item').find('.user-name').text();
        if (confirm(`âš ï¸ Báº¡n cÃ³ cháº¯c muá»‘n cháº·n ${userName}?`)) {
            $(this).closest('.user-item').addClass('blocked');
            $(this).closest('.user-item').find('.user-role').removeClass('admin mod user').addClass('blocked');
            $(this).closest('.user-item').find('.role-badge').html('ðŸš« Blocked');
            alert(`âœ… ÄÃ£ cháº·n ${userName}!`);
        }
    });

    $(document).on('click', '.user-action-btn.unblock', function() {
        const userId = $(this).data('user-id');
        const userName = $(this).closest('.user-item').find('.user-name').text();
        if (confirm(`âœ… Báº¡n cÃ³ cháº¯c muá»‘n bá» cháº·n ${userName}?`)) {
            $(this).closest('.user-item').removeClass('blocked');
            $(this).closest('.user-item').find('.user-role').removeClass('blocked').addClass('user');
            $(this).closest('.user-item').find('.role-badge').html('ðŸ‘¤ User');
            alert(`âœ… ÄÃ£ bá» cháº·n ${userName}!`);
        }
    });

    $(document).on('click', '.user-action-btn.delete', function() {
        const userId = $(this).data('user-id');
        const userName = $(this).closest('.user-item').find('.user-name').text();
        if (confirm(`âš ï¸ Báº¡n cÃ³ cháº¯c muá»‘n xÃ³a ${userName}?\n\nHÃ nh Ä‘á»™ng nÃ y khÃ´ng thá»ƒ hoÃ n tÃ¡c!`)) {
            $(this).closest('.user-item').fadeOut(300, function() {
                $(this).remove();
            });
            alert(`âœ… ÄÃ£ xÃ³a ${userName}!`);
        }
    });

    // ==================== THEME PAGE SYNC ====================
    
    // Sync theme mode selection (light/dark/auto) with app
    $(document).on('click', '.theme-mode-card', function(){
        const mode = $(this).data('mode');
        if (mode === 'light' || mode === 'dark') {
            setTheme(mode);
            // Update active state
            $('.theme-mode-card').removeClass('active');
            $(this).addClass('active');
        }
    });
    
    // Sync theme colors - apply to :root if needed
    $(document).on('click', '.color-scheme', function(){
        const scheme = $(this).data('scheme');
        try { localStorage.setItem('site-color-scheme', scheme); } catch(e){}
        $('.color-scheme').removeClass('active');
        $(this).addClass('active');
    });
    
    // Handle background option changes
    $(document).on('click', '.bg-option', function(){
        const bg = $(this).data('bg');
        try { localStorage.setItem('site-bg-style', bg); } catch(e){}
        $('.bg-option').removeClass('active');
        $(this).addClass('active');
    });
    
    // Handle other theme settings (font, border-radius, etc)
    $(document).on('change', '#font-family, #font-size, #border-radius, #animation-speed', function(){
        const id = $(this).attr('id');
        const val = $(this).val();
        try { localStorage.setItem('site-' + id, val); } catch(e){}
    });
    
    // Handle blur toggle
    $(document).on('click', '#toggle-blur', function(){
        $(this).toggleClass('active');
        const isActive = $(this).hasClass('active');
        try { localStorage.setItem('site-blur', isActive ? 'true' : 'false'); } catch(e){}
    });
    
    // Function to sync theme page UI with current theme state
    function syncThemePageUI() {
        try {
            const savedTheme = localStorage.getItem('site-theme') || 'light';
            $('.theme-mode-card').removeClass('active');
            $('.theme-mode-card[data-mode="' + savedTheme + '"]').addClass('active');
            
            const savedScheme = localStorage.getItem('site-color-scheme');
            if (savedScheme) {
                $('.color-scheme').removeClass('active');
                $('.color-scheme[data-scheme="' + savedScheme + '"]').addClass('active');
            }
            
            const savedBg = localStorage.getItem('site-bg-style');
            if (savedBg) {
                $('.bg-option').removeClass('active');
                $('.bg-option[data-bg="' + savedBg + '"]').addClass('active');
            }
            
            const savedBlur = localStorage.getItem('site-blur');
            if (savedBlur === 'true') {
                $('#toggle-blur').addClass('active');
            } else {
                $('#toggle-blur').removeClass('active');
            }
            
            const savedFont = localStorage.getItem('site-font-family');
            if (savedFont) $('#font-family').val(savedFont);
            
            const savedSize = localStorage.getItem('site-font-size');
            if (savedSize) $('#font-size').val(savedSize);
            
            const savedRadius = localStorage.getItem('site-border-radius');
            if (savedRadius) $('#border-radius').val(savedRadius);
            
            const savedSpeed = localStorage.getItem('site-animation-speed');
            if (savedSpeed) $('#animation-speed').val(savedSpeed);
        } catch(e) {}
    }
    
    // Call on document ready to sync if theme page is active
    if ($('#theme-page').length) {
        syncThemePageUI();
    }
    
    // Re-sync when page becomes active (observer pattern)
    $(document).on('click', 'nav a[href*="/theme"]', function() {
        setTimeout(syncThemePageUI, 100);
    });
    
    // Listen for theme changes dispatched by setTheme() so the theme page UI updates live
    try { window.addEventListener('site-theme-changed', syncThemePageUI); } catch(e) {}
    
    // Load and apply saved theme settings on theme page  
    if ($('#theme-page').length && $('#theme-page').hasClass('active')) {
        try {
            const savedTheme = localStorage.getItem('site-theme');
            if (savedTheme === 'dark') {
                $('.theme-mode-card').removeClass('active');
                $('.theme-mode-card[data-mode="dark"]').addClass('active');
            } else if (savedTheme === 'light') {
                $('.theme-mode-card').removeClass('active');
                $('.theme-mode-card[data-mode="light"]').addClass('active');
            }
            
            const savedScheme = localStorage.getItem('site-color-scheme');
            if (savedScheme) {
                $('.color-scheme').removeClass('active');
                $('.color-scheme[data-scheme="' + savedScheme + '"]').addClass('active');
            }
            
            const savedBg = localStorage.getItem('site-bg-style');
            if (savedBg) {
                $('.bg-option').removeClass('active');
                $('.bg-option[data-bg="' + savedBg + '"]').addClass('active');
            }
            
            const savedBlur = localStorage.getItem('site-blur');
            if (savedBlur === 'true') {
                $('#toggle-blur').addClass('active');
            }
        } catch(e) {}
    }

    // ==================== INITIALIZE ====================
    
    // Check if on profile page
    if ($('#profile-page').length && $('#profile-page').hasClass('active')) {
        loadProfileData();
    }

    // Initialize theme page sync
    if ($('#theme-page').length) {
        syncThemePageUI();
    }

    // Initialize
    renderBotsManagement();
    renderGroups();
    renderFriends();
    checkLoginFromServer();
    loadMyBotsFromAPI(); // Load user's bots instead
    
    // Update rental summary on load
    if ($('#rental-page').length) {
        updateRentalSummary();
    }
    
    // Start payment timer if on payment page
    if ($('#payment-page').length && $('#payment-page').hasClass('active')) {
        startPaymentTimer();
    }
});
