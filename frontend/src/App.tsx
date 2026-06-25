import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { ProtectedRoute } from './core/guards/ProtectedRoute';

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
import { GlobalFinancialSummaryPage } from './pages/Payouts/GlobalFinancialSummaryPage';
import { ChitFinancialSummaryPage } from './pages/Payouts/ChitFinancialSummaryPage';
import { WinnerPayoutListPage } from './pages/Payouts/WinnerPayoutListPage';
import { WinnerPayoutDetailPage } from './pages/Payouts/WinnerPayoutDetailPage';

function App() {
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
            
            {/* Phase 6: Financial Summary & Closure */}
            <Route path="/organizer/financial-summary" element={<GlobalFinancialSummaryPage />} />
            <Route path="/organizer/chit-groups/:chitGroupId/financial-summary" element={<ChitFinancialSummaryPage />} />
            
            {/* Phase 6.1: Winner Payout Receipt & Tracking */}
            <Route path="/organizer/winner-payouts" element={<WinnerPayoutListPage />} />
            <Route path="/organizer/winner-payouts/:payoutId" element={<WinnerPayoutDetailPage />} />
          </Route>

          {/* Admin Routes */}
          <Route element={<ProtectedRoute allowedRoles={['ADMIN']} />}>
            <Route path="/admin/organizers" element={<OrganizerList />} />
            <Route path="/admin/organizers/new" element={<CreateOrganizer />} />
            <Route path="/admin/organizers/:id" element={<div className="p-4">Organizer Detail Placeholder</div>} />
          </Route>
        </Route>
        
        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
