<template>
  <div id="app">
    <header class="app-header">
      <h1>Beancount记账</h1>
    </header>
    <main class="app-main">
      <router-view />
    </main>
    <nav class="app-nav">
      <router-link to="/" class="nav-item">
        <span>📷</span>
        <span>记账</span>
      </router-link>
      <router-link to="/balance" class="nav-item">
        <span>💰</span>
        <span>余额</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
</script>

<style scoped>
.app-header {
  background: #4DBA87;
  color: white;
  padding: 1rem;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.app-header h1 {
  font-size: 1.125rem;
  font-weight: 600;
}

@media (min-width: 768px) {
  .app-header {
    padding: 1.5rem;
  }
  
  .app-header h1 {
    font-size: 1.5rem;
  }
}

.app-main {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 70px;
}

@media (min-width: 768px) {
  .app-main {
    padding-bottom: 80px;
  }
}

.app-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  display: flex;
  justify-content: space-around;
  padding: 0.5rem;
  box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
  z-index: 100;
}

@media (min-width: 768px) {
  .app-nav {
    padding: 0.75rem;
  }
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem 1rem;
  text-decoration: none;
  color: #666;
  transition: color 0.3s;
  min-width: 60px;
  border-radius: 8px;
}

.nav-item:hover {
  background: #f5f5f5;
}

.nav-item span:first-child {
  font-size: 1.25rem;
  margin-bottom: 0.25rem;
}

.nav-item span:last-child {
  font-size: 0.75rem;
  font-weight: 500;
}

@media (min-width: 768px) {
  .nav-item {
    padding: 0.75rem 1.5rem;
  }
  
  .nav-item span:first-child {
    font-size: 1.5rem;
  }
  
  .nav-item span:last-child {
    font-size: 0.875rem;
  }
}

.nav-item.router-link-active {
  color: #4DBA87;
  background: rgba(77, 186, 135, 0.1);
}
</style>
