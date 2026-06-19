# Business Rules

1. A chit group has fixed members and duration.

2. One member can win only once in a chit group (`won_status` set to true upon winning, preventing future bids).

3. Auction is conducted before monthly collection. Dues for the month are generated only after the auction has completed and the bonus has been computed.

4. Winner receives:
   `Chit Amount - Maintenance Charge - Winning Bid`

5. Winning bid amount is distributed equally among all members as bonus (dividend).

6. Member Payable Amount:
   `Monthly Installment - Bonus`

7. Winner continues paying installments until chit completion.

8. Maintainer (Organizer) can run multiple chit groups.

9. Member belongs to only one position in a chit group. Each member is assigned a unique fixed seat number (`position_no` e.g., 1, 2, ... N) upon joining the group.

10. Late payment may incur penalty interest.

11. Membership can be cancelled by the maintainer.

12. Every collection must generate a receipt and a matching passbook entry.

---

## Bidding Constraints
*   **Active Status:** Only active members with cleared historical dues can bid.
*   **Bidding Exclusivity:** Non-prized members can bid. Once a member has won an auction, their eligibility to bid in subsequent months is terminated.
*   **Auction Context:** An auction session must be conducted and closed to determine the monthly bonus *before* any subscriber payments can be collected for that month.
*   **Dividends:** The total auction discount (winning bid amount) minus the foreman's maintenance charge is shared equally among all members as a bonus credit, reducing their net dues.
