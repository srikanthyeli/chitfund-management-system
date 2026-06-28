import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { ProtectedRoute } from './core/guards/ProtectedRoute';
import { useTheme } from './core/useTheme';

// Pages
import { Login } from './pages/Auth/Login';
import { OrganizerDashboard } from './pages/Dashboard/OrganizerDashboard';
import { OrganizerList } from './pages/Admin/OrganizerList';
import { CreateOrganizer } from './pages/Admin/CreateOrganizer';

// Member management pages
import { MemberList } from './pages/Members/MemberList';
import { MemberCreate } from './pages/Members/MemberCreate';
import { MemberDetail } from './pages/Members/MemberDetail';
import { MemberEdit } from './pages/Members/MemberEdit';

// Chit group management pages
import { ChitGroupList } from './pages/ChitGroups/ChitGroupList';
import { ChitGroupCreate } from './pages/ChitGroups/ChitGroupCreate';
import { ChitGroupDetail } from './pages/ChitGroups/ChitGroupDetail';
import { ChitGroupEdit } from './pages/ChitGroups/ChitGroupEdit';

// Auction management pages
import { AuctionsPage } from './pages/Auctions/AuctionsPage';
import { AuctionDetailPage } from './pages/Auctions/AuctionDetailPage';

// Collection management pages
import { CollectionsPage } from './pages/Collections/CollectionsPage';
import { CollectionDetailsPage } from './pages/Collections/CollectionDetailsPage';
import { MemberPassbookPage } from './pages/Collections/MemberPassbookPage';
import { WinnerPayoutListPage } from './pages/Payouts/WinnerPayoutListPage';
import { WinnerPayoutDetailPage } from './pages/Payouts/WinnerPayoutDetailPage';
// Financial Utilities — lazy loaded
const BondInterestCalculatorPage = lazy(() =>
  import('./pages/FinancialUtilities/BondInterestCalculatorPage').then((m) => ({ default: m.BondInterestCalculatorPage }))
);

// Reports pages
import { ReportsDashboard } from './pages/Reports/ReportsDashboard';
import { CollectionReport } from './pages/Reports/CollectionReport';
import { PendingCollectionReport } from './pages/Reports/PendingCollectionReport';
import { AuctionReport, WinnerPayoutReport, MemberFinancialReport, OrganizerFinancialReport, ChitPerformanceReport } from './pages/Reports/OtherReports';

// Member Portal Pages
import { MemberDashboardPage } from './features/member-portal/pages/MemberDashboardPage';
import { MyChitsPage } from './features/member-portal/pages/MyChitsPage';
import { MyPaymentsPage } from './features/member-portal/pages/MyPaymentsPage';
import { MyReceiptsPage } from './features/member-portal/pages/MyReceiptsPage';
import { MemberPassbookPage as MemberPortalPassbookPage } from './features/member-portal/pages/MemberPassbookPage';
import { MemberAuctionResultsPage } from './features/member-portal/pages/MemberAuctionResultsPage';
import { MyWinnerPayoutsPage } from './features/member-portal/pages/MyWinnerPayoutsPage';
import { MemberNotificationsPage } from './features/member-portal/pages/MemberNotificationsPage';
import { MemberProfilePage } from './features/member-portal/pages/MemberProfilePage';
import { MyChitDetailPage } from './features/member-portal/pages/MyChitDetailPage';

function App() {
  useTheme(); // initialize theme from localStorage on every page
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        
        {/* Protected Routes inside Layout */}
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          
          {/* Organizer Routes */}
          <Route element={<ProtectedRoute allowedRoles={['ORGANIZER']} />}>
            <Route path="/organizer/dashboard" element={<OrganizerDashboard />} />
            <Route path="/dashboard" element={<Navigate to="/organizer/dashboard" replace />} />
            <Route
              path="/dashboard/bond-calculator"
              element={
                <Suspense fallback={<div className="flex justify-center p-8 text-gray-400">Loading…</div>}>
                  <BondInterestCalculatorPage />
                </Suspense>
              }
            />
            
            {/* Member management routes */}
            <Route path="/organizer/members" element={<MemberList />} />
            <Route path="/organizer/members/new" element={<MemberCreate />} />
            <Route path="/organizer/members/:id" element={<MemberDetail />} />
            <Route path="/organizer/members/:id/edit" element={<MemberEdit />} />

            {/* Chit group routes */}
            <Route path="/organizer/chit-groups" element={<ChitGroupList />} />
            <Route path="/organizer/chit-groups/new" element={<ChitGroupCreate />} />
            <Route path="/organizer/chit-groups/:id" element={<ChitGroupDetail />} />
            <Route path="/organizer/chit-groups/:id/edit" element={<ChitGroupEdit />} />
            <Route path="/chits" element={<Navigate to="/organizer/chit-groups" replace />} />

            {/* Auction routes */}
            <Route path="/organizer/chit-groups/:id/auctions" element={<AuctionsPage />} />
            <Route path="/organizer/chit-groups/:id/auctions/:auctionId" element={<AuctionDetailPage />} />

            {/* Collection routes */}
            <Route path="/organizer/collections" element={<CollectionsPage />} />
            <Route path="/organizer/chit-groups/:chitGroupId/auctions/:auctionId/collections" element={<CollectionDetailsPage />} />
            <Route path="/organizer/members/:memberId/passbook" element={<MemberPassbookPage />} />
            
            {/* Phase 6.1: Winner Payout Receipt & Tracking */}
            <Route path="/organizer/winner-payouts" element={<WinnerPayoutListPage />} />
            <Route path="/organizer/winner-payouts/:payoutId" element={<WinnerPayoutDetailPage />} />

            {/* Phase 8: Reports & Analytics */}
            <Route path="/organizer/reports" element={<ReportsDashboard />} />
            <Route path="/organizer/reports/collections" element={<CollectionReport />} />
            <Route path="/organizer/reports/pending-collections" element={<PendingCollectionReport />} />
            <Route path="/organizer/reports/auctions" element={<AuctionReport />} />
            <Route path="/organizer/reports/winner-payouts" element={<WinnerPayoutReport />} />
            <Route path="/organizer/reports/member-financial" element={<MemberFinancialReport />} />
            <Route path="/organizer/reports/organizer-financial" element={<OrganizerFinancialReport />} />
            <Route path="/organizer/reports/chit-performance" element={<ChitPerformanceReport />} />
          </Route>

          {/* Admin Routes */}
          <Route element={<ProtectedRoute allowedRoles={['ADMIN']} />}>
            <Route path="/admin/organizers" element={<OrganizerList />} />
            <Route path="/admin/organizers/new" element={<CreateOrganizer />} />
            <Route path="/admin/organizers/:id" element={<div className="p-4">Organizer Detail Placeholder</div>} />
          </Route>

          {/* Member Portal Routes */}
          <Route element={<ProtectedRoute allowedRoles={['MEMBER']} />}>
            <Route path="/member/dashboard" element={<MemberDashboardPage />} />
            <Route path="/member/chits" element={<MyChitsPage />} />
            <Route path="/member/chits/:id" element={<MyChitDetailPage />} />
            <Route path="/member/payments" element={<MyPaymentsPage />} />
            <Route path="/member/receipts" element={<MyReceiptsPage />} />
            <Route path="/member/passbook" element={<MemberPortalPassbookPage />} />
            <Route path="/member/auction-results" element={<MemberAuctionResultsPage />} />
            <Route path="/member/winner-payouts" element={<MyWinnerPayoutsPage />} />
            <Route path="/member/notifications" element={<MemberNotificationsPage />} />
            <Route path="/member/profile" element={<MemberProfilePage />} />
          </Route>
        </Route>
        
        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
