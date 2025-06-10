import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'
import Login from '../pages/Login.vue'

// 布局组件（后续创建）
const AdminLayout = () => import('../layouts/AdminLayout.vue')
const TeacherLayout = () => import('../layouts/TeacherLayout.vue')
const StudentLayout = () => import('../layouts/StudentLayout.vue')

// 学生页面
const StudentExercises = () => import('../pages/student/Exercises.vue')
const StudentExerciseDetail = () => import('../pages/student/ExerciseDetail.vue')
const StudentOperationLogs = () => import('../pages/student/OperationLogs.vue')
const StudentProfile = () => import('../pages/student/Profile.vue')

// 教师页面
const TeacherExercises = () => import('../pages/teacher/Exercises.vue')
const TeacherExerciseDetail = () => import('../pages/teacher/ExerciseDetail.vue')
const TeacherOperationLogs = () => import('../pages/teacher/OperationLogs.vue')
const TeacherManagement = () => import('../pages/teacher/Management.vue')
const TeacherMaintenance = () => import('../pages/teacher/Maintenance.vue')
const TeacherProfile = () => import('../pages/teacher/Profile.vue')

// 管理员页面
const AdminExercises = () => import('../pages/admin/Exercises.vue')
const AdminExerciseDetail = () => import('../pages/admin/ExerciseDetail.vue')
const AdminOperationLogs = () => import('../pages/admin/OperationLogs.vue')
const AdminManagement = () => import('../pages/admin/Management.vue')
const AdminMaintenance = () => import('../pages/admin/Maintenance.vue')
const AdminSystem = () => import('../pages/admin/System.vue')

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    redirect: '/login'
  },
  
  // 学生路由
  {
    path: '/student',
    component: StudentLayout,
    meta: { requiresAuth: true, role: 'student' },
    children: [
      {
        path: 'exercises',
        name: 'StudentExercises',
        component: StudentExercises,
        meta: { title: '练习' }
      },
      {
        path: 'exercise/:id',
        name: 'StudentExerciseDetail',
        component: StudentExerciseDetail,
        meta: { title: '练习详情' }
      },
      {
        path: 'operation-logs',
        name: 'StudentOperationLogs',
        component: StudentOperationLogs,
        meta: { title: '操作记录' }
      },
      {
        path: 'profile',
        name: 'StudentProfile',
        component: StudentProfile,
        meta: { title: '个人信息' }
      }
    ]
  },
  
  // 教师路由
  {
    path: '/teacher',
    component: TeacherLayout,
    meta: { requiresAuth: true, role: 'teacher' },
    children: [
      {
        path: 'exercises',
        name: 'TeacherExercises',
        component: TeacherExercises,
        meta: { title: '练习' }
      },
      {
        path: 'exercise/:id',
        name: 'TeacherExerciseDetail',
        component: TeacherExerciseDetail,
        meta: { title: '练习详情' }
      },
      {
        path: 'operation-logs',
        name: 'TeacherOperationLogs',
        component: TeacherOperationLogs,
        meta: { title: '操作记录' }
      },
      {
        path: 'management',
        name: 'TeacherManagement',
        component: TeacherManagement,
        meta: { title: '管理' }
      },
      {
        path: 'maintenance',
        name: 'TeacherMaintenance',
        component: TeacherMaintenance,
        meta: { title: '维护' }
      },
      {
        path: 'profile',
        name: 'TeacherProfile',
        component: TeacherProfile,
        meta: { title: '个人信息' }
      }
    ]
  },
  
  // 管理员路由
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      {
        path: 'exercises',
        name: 'AdminExercises',
        component: AdminExercises,
        meta: { title: '练习' }
      },
      {
        path: 'exercise/:id',
        name: 'AdminExerciseDetail',
        component: AdminExerciseDetail,
        meta: { title: '练习详情' }
      },
      {
        path: 'operation-logs',
        name: 'AdminOperationLogs',
        component: AdminOperationLogs,
        meta: { title: '操作记录' }
      },
      {
        path: 'management',
        name: 'AdminManagement',
        component: AdminManagement,
        meta: { title: '管理' }
      },
      {
        path: 'maintenance',
        name: 'AdminMaintenance',
        component: AdminMaintenance,
        meta: { title: '维护' }
      },
      {
        path: 'system',
        name: 'AdminSystem',
        component: AdminSystem,
        meta: { title: '系统' }
      }
    ]
  },
  
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiredRole = to.matched.find(record => record.meta.role)?.meta.role
  
  // 如果有token但没有用户信息，尝试恢复会话
  if (authStore.token && !authStore.user) {
    await authStore.restoreSession()
  }
  
  if (requiresAuth && !authStore.isAuthenticated) {
    // 需要认证但未登录，重定向到登录页
    next('/login')
  } else if (requiresAuth && requiredRole && authStore.userRole !== requiredRole && authStore.userRole !== 'admin') {
    // 需要特定角色但没有权限（管理员可以访问所有页面）
    next(`/${authStore.userRole}/exercises`)
  } else {
    // 已登录且有权限，或不需要认证
    next()
  }
})

export default router 