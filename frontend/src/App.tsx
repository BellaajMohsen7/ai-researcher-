import { RouterProvider, createHashRouter } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import CategoryView from './pages/CategoryView';
import WeeklyReport from './pages/WeeklyReport';
import Search from './pages/Search';
import Settings from './pages/Settings';

const router = createHashRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'category/:cat', element: <CategoryView /> },
      { path: 'report', element: <WeeklyReport /> },
      { path: 'search', element: <Search /> },
      { path: 'settings', element: <Settings /> },
    ],
  },
]);

export default function App() {
  return (
    <>
      <RouterProvider router={router} />
      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: '#1b2028',
            color: '#f1f3fc',
            border: '1px solid #44484f30',
          },
        }}
      />
    </>
  );
}
