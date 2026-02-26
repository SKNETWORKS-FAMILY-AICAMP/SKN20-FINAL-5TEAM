<template>
  <div class="log-viewer-container bg-gray-50 min-h-screen text-gray-800 font-sans">
    <div v-if="!isLoggedIn" class="login-modal flex items-center justify-center min-h-screen">
      <div class="login-box bg-white border border-gray-200 p-8 rounded-xl shadow-lg w-96 max-w-full">
        <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">Admin Console</h2>
        
        <form @submit.prevent="handleLogin" class="space-y-5">
          <div>
            <label class="block text-gray-600 text-sm font-bold mb-2">Admin Email</label>
            <input 
              v-model="username" 
              type="text" 
              class="w-full bg-gray-100 text-gray-800 border border-gray-300 rounded-lg px-4 py-2 outline-none focus:border-blue-500 focus:bg-white transition-colors" 
              placeholder="admin@admin.com" 
              required
            />
          </div>
          <div>
            <label class="block text-gray-600 text-sm font-bold mb-2">Password</label>
            <input 
              v-model="password" 
              type="password" 
              class="w-full bg-gray-100 text-gray-800 border border-gray-300 rounded-lg px-4 py-2 outline-none focus:border-blue-500 focus:bg-white transition-colors" 
              placeholder="Password" 
              required
            />
          </div>
          <p v-if="loginError" class="text-red-500 text-sm mt-2">{{ loginError }}</p>
          <div class="mt-6">
            <button 
              type="submit" 
              class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2.5 px-4 rounded-lg transition-colors shadow-sm"
              :disabled="isLoggingIn"
            >
              {{ isLoggingIn ? 'Authenticating...' : 'Sign In' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 로그 뷰어 대시보드 화면 -->
    <div v-else class="flex flex-col h-screen overflow-hidden p-4 md:p-6 space-y-4 md:space-y-6 max-w-[1600px] mx-auto box-border">
      
      <!-- 헤더 -->
      <header class="flex flex-col md:flex-row justify-between items-start md:items-center bg-white p-3 md:p-4 rounded-xl shadow-sm border border-gray-200 gap-4 md:gap-0">
        <div class="flex flex-col lg:flex-row lg:items-center gap-3 lg:gap-6 w-full md:w-auto">
          <div>
            <h1 class="text-xl md:text-2xl font-bold text-gray-800 flex items-center">
              <activity class="w-5 h-5 md:w-6 md:h-6 mr-2 text-blue-600" />
              시스템 모니터링 대시보드
            </h1>
            <p class="text-gray-500 text-xs md:text-sm mt-1">서버 상태 및 에러 로그 과거 이력 모니터링</p>
          </div>
          <!-- 시간 범위 선택 -->
          <div class="flex items-center bg-gray-100/80 rounded-lg p-1 border border-gray-200 shadow-inner flex-shrink-0 self-start lg:self-auto">
            <label for="timeRange" class="text-xs md:text-sm text-gray-500 font-extrabold px-2 md:px-3 flex items-center whitespace-nowrap">
              <activity class="w-3.5 h-3.5 md:w-4 md:h-4 mr-1 md:mr-1.5 text-gray-400"/>
              기간 조회
            </label>
            <select 
              id="timeRange" 
              v-model="timeRange" 
              @change="fetchServerStatus"
              class="bg-white border-transparent text-blue-700 font-bold text-xs md:text-sm rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm block py-1.5 px-2 md:px-3 cursor-pointer outline-none transition-all appearance-none pr-8 relative"
              style="background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%232563EB%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right .7rem top 50%; background-size: .65rem auto;"
            >
              <option value="24h">최근 24시간</option>
              <option value="3d">최근 3일</option>
              <option value="7d">최근 1주일</option>
            </select>
          </div>
        </div>
        <div class="actions flex space-x-2 md:space-x-3 items-center self-end md:self-auto flex-shrink-0">
          <button 
            @click="refreshAll" 
            class="bg-white border border-gray-200 hover:bg-blue-50 hover:border-blue-300 hover:text-blue-700 text-gray-700 font-bold py-1.5 px-3 md:py-2 md:px-4 rounded-lg flex items-center transition-all duration-200 shadow-sm group text-sm md:text-base whitespace-nowrap flex-shrink-0"
            :disabled="isLoading || isLoadingStatus"
          >
            <refresh-cw class="w-3.5 h-3.5 md:w-4 md:h-4 mr-1.5 md:mr-2 text-gray-400 group-hover:text-blue-500 transition-colors" :class="{ 'animate-spin text-blue-500': (isLoading || isLoadingStatus) }" />
            새로고침
          </button>
          <button 
            @click="logout" 
            class="bg-slate-800 border border-slate-700 hover:bg-red-600 hover:border-red-500 text-white font-bold py-1.5 px-3 md:py-2 md:px-4 rounded-lg flex items-center transition-all duration-200 shadow-sm shadow-slate-200 group text-sm md:text-base whitespace-nowrap flex-shrink-0"
          >
            <log-out class="w-3.5 h-3.5 md:w-4 md:h-4 mr-1.5 md:mr-2 text-slate-300 group-hover:text-white transition-colors" />
            로그아웃
          </button>
        </div>
      </header>

      <!-- 상단 차트 영역 -->
      <section class="chart-section bg-white p-4 md:p-5 rounded-xl shadow-sm border border-gray-200 flex flex-col flex-shrink-0" style="height: 30vh; min-height: 250px; max-height: 320px;">
        <div class="flex items-center justify-between mb-4 border-b border-gray-100 pb-3">
          <h2 class="text-xl font-extrabold text-gray-800 flex items-center tracking-tight">
            <div class="bg-blue-100 p-2 rounded-lg mr-3 shadow-inner">
              <bar-chart2 class="w-5 h-5 text-blue-600" />
            </div>
            최근 24시간 오류 및 트래픽 현황
            <span class="ml-3 px-2.5 py-0.5 rounded-full bg-green-100 text-green-700 text-xs font-bold border border-green-200 flex items-center">
              <span class="w-1.5 h-1.5 rounded-full bg-green-500 mr-1.5 animate-pulse"></span>
              LIVE
            </span>
          </h2>
        </div>
        <div class="relative w-full h-52">
          <canvas ref="chartCanvas"></canvas>
          <div v-if="isLoadingStatus" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-70 text-gray-500">
            데이터를 불러오는 중입니다...
          </div>
        </div>
      </section>

      <!-- 하단 로그 뷰어 & 아카이브 패널 -->
      <section class="flex flex-col space-y-4 md:space-y-6 flex-grow overflow-hidden pb-2 md:pb-4">
        
        <!-- 상단: 현재 / 과거 로그 상세 -->
        <div class="current-log-section w-full flex-1 flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden min-h-0">
            <div class="header px-5 py-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
              <div>
                <h2 class="text-lg font-bold text-gray-800 flex items-center">
                  <terminal class="w-5 h-5 mr-2" :class="viewingMode === 'current' ? 'text-green-600' : 'text-purple-600'" />
                  {{ viewingMode === 'current' ? '현재 실시간 에러 로그' : '아카이브 파일: ' + viewingFile }}
                </h2>
              </div>
              <div class="actions flex space-x-2">
                <button 
                  v-if="viewingMode === 'archive'"
                  @click="switchToCurrentLog" 
                  class="bg-white border border-purple-300 hover:bg-purple-50 text-purple-700 text-sm font-semibold py-1.5 px-3 rounded-md transition-colors shadow-sm"
                >
                  현재 시간으로 복귀
                </button>
              </div>
            </div>

            <div class="bg-gray-900 flex-grow overflow-hidden flex flex-col relative">
               <div v-if="saveSuccessMsg" class="absolute top-4 right-4 bg-green-500 text-white px-4 py-2 rounded shadow-md opacity-90 transition-opacity z-10 text-sm">
                 {{ saveSuccessMsg }}
               </div>

              <div v-if="isLoading && !logs" class="flex items-center justify-center flex-grow text-gray-400">
                로딩 중...
              </div>
              <div v-else-if="logsError" class="flex items-center justify-center flex-grow text-red-400">
                {{ logsError }}
              </div>
              <div v-else-if="!logs" class="flex items-center justify-center flex-grow text-gray-500">
                기록된 로그가 없습니다.
              </div>
              <div v-else class="log-lines-container overflow-y-auto overflow-x-hidden flex-grow w-full h-full text-sm font-mono text-gray-300 p-4 pb-10 relative">
                <div 
                  v-for="(line, idx) in logLines" 
                  :key="idx" 
                  :id="'log-line-' + idx"
                  class="px-3 py-0.5 whitespace-pre-wrap break-words border-l-4 transition-colors"
                  :class="highlightedLine === idx ? 'bg-yellow-100 border-yellow-500 text-gray-900' : 'border-transparent hover:bg-gray-800'"
                >
                  {{ line }}
                </div>
              </div>
            </div>
        </div>

        <!-- 하단: 과거 로그 사이드바 -->
        <div class="archive-sidebar w-full flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden h-64 flex-shrink-0">
          <div class="px-5 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
            <h2 class="text-lg font-bold text-gray-800 flex items-center">
              <archive class="w-5 h-5 mr-2 text-gray-500" />
              과거 로그 아카이브
            </h2>
          </div>
          
          <div class="archive-list overflow-y-auto flex-grow p-3 bg-white">
            <div v-if="isLoadingArchives" class="text-center text-gray-500 my-4 text-sm">목록 가져오는 중...</div>
            <div v-else-if="archives.length === 0" class="text-center text-gray-400 my-8 text-sm">보관된 로그가 없습니다.</div>
            <ul v-else class="space-y-2">
              <li 
                v-for="archive in archives" 
                :key="archive.filename"
                @click="fetchArchiveDetail(archive.filename)"
                class="border p-3 rounded-lg cursor-pointer transition-all flex flex-col group"
                :class="[
                  viewingFile === archive.filename 
                    ? 'border-purple-500 bg-purple-50 shadow-sm' 
                    : 'border-gray-200 hover:border-blue-300 hover:bg-blue-50'
                ]"
              >
                <div class="flex items-start">
                  <file-text class="w-4 h-4 mr-2 mt-0.5" :class="viewingFile === archive.filename ? 'text-purple-600' : 'text-gray-400 group-hover:text-blue-500'" />
                  <div>
                    <span class="text-sm font-semibold" :class="viewingFile === archive.filename ? 'text-purple-800' : 'text-gray-700'">{{ archive.filename }}</span>
                    <div class="flex items-center mt-1 text-xs text-gray-500">
                      <span>{{ archive.modified_at }}</span>
                      <span class="mx-2">•</span>
                      <span>{{ Math.round(archive.size / 1024) }} KB</span>
                    </div>
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import axios from 'axios'
import { AlertCircle, Activity, BarChart2, Terminal, Archive, FileText, RefreshCw, LogOut } from 'lucide-vue-next'
import Chart from 'chart.js/auto'

const isLoggedIn = ref(false)
const username = ref('')
const password = ref('')
const loginError = ref('')
const isLoggingIn = ref(false)

const logs = ref('')
const logsError = ref('')
const isLoading = ref(false)
const authToken = ref('')

// 상태
const timeRange = ref('24h') // 24h, 3d, 7d

// 로그를 줄 단위로 분할하여 렌더링하고 검색하기 위함
const logLines = computed(() => {
  return logs.value ? logs.value.split('\n') : []
})
const highlightedLine = ref(-1)

const archives = ref([])
const isLoadingArchives = ref(false)
const isSaving = ref(false)
const saveSuccessMsg = ref('')

const viewingMode = ref('current') // 'current' or 'archive'
const viewingFile = ref('')

// Chart.js 관련
const chartCanvas = ref(null)
const chartInstance = ref(null)
const isLoadingStatus = ref(false)

// 이미 세션/로컬에 저장된 토큰이 있는지 확인
onMounted(() => {
  const savedToken = sessionStorage.getItem('adminToken')
  if (savedToken) {
    authToken.value = savedToken
    isLoggedIn.value = true
    initDashboard()
  }
})

onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.destroy()
  }
})

const initDashboard = () => {
  fetchLogs()
  fetchArchiveList()
  fetchServerStatus()
}

const refreshAll = () => {
  if (viewingMode.value === 'current') {
    fetchLogs()
  } else {
    fetchArchiveDetail(viewingFile.value)
  }
  fetchArchiveList()
  fetchServerStatus()
}

const handleLogin = async () => {
  loginError.value = ''
  isLoggingIn.value = true
  
  try {
    const response = await axios.post('/api/core/admin/login/', {
      username: username.value,
      password: password.value
    })
    
    if (response.data.token) {
      authToken.value = response.data.token
      sessionStorage.setItem('adminToken', response.data.token)
      isLoggedIn.value = true
      nextTick(() => {
        initDashboard()
      })
    }
  } catch (err) {
    loginError.value = err.response?.data?.error || '로그인에 실패했습니다.'
  } finally {
    isLoggingIn.value = false
  }
}

const logout = () => {
  authToken.value = ''
  sessionStorage.removeItem('adminToken')
  isLoggedIn.value = false
  logs.value = ''
  if (chartInstance.value) {
    chartInstance.value.destroy()
    chartInstance.value = null
  }
}

const fetchLogs = async () => {
  if (!authToken.value) return
  
  isLoading.value = true
  logsError.value = ''
  
  try {
    const response = await axios.get('/api/core/admin/logs/', {
      headers: {
        Authorization: `Bearer ${authToken.value}`
      }
    })
    
    logs.value = response.data.logs
    highlightedLine.value = -1 // 하이라이트 초기화
    
    // 가져온 즉시 스크롤을 맨 아래로 이동
    nextTick(() => {
       const container = document.querySelector('.log-lines-container')
       if (container) {
         container.scrollTop = container.scrollHeight
       }
    })
    
  } catch (err) {
    if (err.response?.status === 401) {
       logout()
       loginError.value = '세션이 만료되었습니다. 다시 로그인해주세요.'
    } else {
       logsError.value = '로그를 불러오는 데 실패했습니다: ' + (err.response?.data?.error || err.message)
    }
  } finally {
    isLoading.value = false
  }
}

const fetchArchiveList = async () => {
  if (!authToken.value) return
  isLoadingArchives.value = true
  
  try {
    const response = await axios.get('/api/core/admin/logs/archives/', {
      headers: { Authorization: `Bearer ${authToken.value}` }
    })
    archives.value = response.data.archives
  } catch (err) {
    console.error("아카이브 목록 조실패:", err)
  } finally {
    isLoadingArchives.value = false
  }
}

const fetchArchiveDetail = async (filename) => {
  if (!authToken.value) return
  isLoading.value = true
  logsError.value = ''
  
  try {
    const response = await axios.get(`/api/core/admin/logs/archives/${filename}/`, {
      headers: { Authorization: `Bearer ${authToken.value}` }
    })
    
    logs.value = response.data.logs
    viewingMode.value = 'archive'
    viewingFile.value = filename
    highlightedLine.value = -1 // 초기화
    
    nextTick(() => {
       const container = document.querySelector('.log-lines-container')
       if (container) container.scrollTop = 0
    })
  } catch (err) {
    if (err.response?.status === 401) {
       logout()
    } else {
       logsError.value = `(${filename}) 불러오기 실패: ` + (err.response?.data?.error || err.message)
    }
  } finally {
    isLoading.value = false
  }
}

const saveCurrentLog = async () => {
  if (!authToken.value || isSaving.value) return
  isSaving.value = true
  
  try {
    const response = await axios.post('/api/core/admin/logs/save/', {}, {
      headers: { Authorization: `Bearer ${authToken.value}` }
    })
    
    saveSuccessMsg.value = `정상적으로 보관되었습니다 (${response.data.archive_filename})`
    setTimeout(() => { saveSuccessMsg.value = '' }, 3000)
    
    // 리스트 새로고침
    fetchArchiveList()
  } catch (err) {
    alert("저장에 실패했습니다: " + (err.response?.data?.error || err.message))
  } finally {
    isSaving.value = false
  }
}

const switchToCurrentLog = () => {
  viewingMode.value = 'current'
  viewingFile.value = ''
  highlightedLine.value = -1
  fetchLogs()
}

const scrollToLogLine = (searchPrefix) => {
  // searchPrefix 예: "2026-02-26 09:"
  const lines = logLines.value
  const targetIndex = lines.findIndex(line => line.includes(searchPrefix))
  
  if (targetIndex !== -1) {
    highlightedLine.value = targetIndex
    const element = document.getElementById(`log-line-${targetIndex}`)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' })
      // 3초 후 하이라이트 해제
      setTimeout(() => {
        if (highlightedLine.value === targetIndex) {
          highlightedLine.value = -1
        }
      }, 3000)
    }
  } else {
    // 해당 에러 로그가 없을 경우 (예: info 로그만 있거나 덮어써진 경우)
    alert("해당 시간대의 에러 로그를 찾을 수 없습니다.")
  }
}

const fetchServerStatus = async () => {
  if (!authToken.value) return
  isLoadingStatus.value = true
  
  try {
    const response = await axios.get(`/api/core/admin/server-status/?range=${timeRange.value}`, {
      headers: { Authorization: `Bearer ${authToken.value}` }
    })
    
    renderChart(response.data)
  } catch (err) {
    console.error("서버 상태 그래프 조회 실패:", err)
  } finally {
    isLoadingStatus.value = false
  }
}

const renderChart = (data) => {
  if (!chartCanvas.value) return
  
  if (chartInstance.value) {
    chartInstance.value.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')
  
  chartInstance.value = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: [
        {
          label: '에러 발생 건수 (Error Count)',
          data: data.error_counts,
          borderColor: '#ef4444', // red-500
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          borderWidth: 2,
          pointBackgroundColor: '#ef4444',
          pointRadius: function(context) {
             const value = context.dataset.data[context.dataIndex];
             return value > 0 ? 5 : 2; // 에러가 있는 지점은 더 크게 표시
          },
          tension: 0.3,
          yAxisID: 'y1'
        },
        {
          label: '시스템 대략적 트래픽 (System Load)',
          data: data.traffic_loads,
          borderColor: '#3b82f6', // blue-500
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          borderWidth: 2,
          fill: true,
          pointRadius: 0,
          tension: 0.4,
          yAxisID: 'y2'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      onClick: (e, elements) => {
        // 데이터 포인트를 클릭했을 때 로그 스크롤 이벤트 발생
        if (elements.length > 0) {
          const dataIndex = elements[0].index
          const fullLabel = data.full_labels[dataIndex] // "2026-02-26 09:00"
          
          if (data.error_counts[dataIndex] === 0) return
          
          // 우리가 찾을 로그의 시작 형식 (예: 날짜와 "시간:" 까지)
          // 3d, 7d와 같이 간격이 3시간/6시간인 경우 해당 시간의 정시 부근에서 처음 발견된 곳으로 스크롤됨
          const searchPrefix = fullLabel.slice(0, 13) + ":"
          scrollToLogLine(searchPrefix)
        }
      },
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            boxWidth: 8
          }
        },
        tooltip: {
          backgroundColor: 'rgba(17, 24, 39, 0.9)', // gray-900
          titleFont: { size: 13 },
          bodyFont: { size: 13 },
          padding: 10,
          cornerRadius: 4,
          displayColors: true
        }
      },
      scales: {
        x: {
          grid: {
            display: false,
          },
          ticks: {
            font: { size: 11 },
            color: '#6b7280' // gray-500
          }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'left',
          title: {
            display: true,
            text: 'Errors',
            color: '#ef4444',
            font: { size: 11, weight: 'bold' }
          },
          grid: {
            color: '#f3f4f6', // gray-100
          },
          min: 0,
          suggestedMax: 10
        },
        y2: {
          type: 'linear',
          display: true,
          position: 'right',
          title: {
            display: true,
            text: 'System Load (%)',
            color: '#3b82f6',
            font: { size: 11, weight: 'bold' }
          },
          grid: {
            drawOnChartArea: false, 
          },
          min: 0,
          max: 100
        },
      }
    }
  })
}
</script>

<style scoped>
/* Scoped styles are minimal now as Tailwind classes handle most styling */
</style>
