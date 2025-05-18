// 平滑滚动效果
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        
        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 100,
                behavior: 'smooth'
            });
        }
    });
});

// 展示卡片动画效果
const exhibitCards = document.querySelectorAll('.exhibit-card');
const featureItems = document.querySelectorAll('.feature-item');

// 监听滚动事件，为可见元素添加动画
function checkVisibility() {
    const triggerBottom = window.innerHeight * 0.8;
    
    exhibitCards.forEach(card => {
        const cardTop = card.getBoundingClientRect().top;
        
        if (cardTop < triggerBottom) {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }
    });
    
    featureItems.forEach(item => {
        const itemTop = item.getBoundingClientRect().top;
        
        if (itemTop < triggerBottom) {
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }
    });
}

// 初始化样式
exhibitCards.forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
});

featureItems.forEach(item => {
    item.style.opacity = '0';
    item.style.transform = 'translateY(20px)';
    item.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
});

// 页面加载时检查一次可见性
window.addEventListener('load', checkVisibility);
// 滚动时检查可见性
window.addEventListener('scroll', checkVisibility); 