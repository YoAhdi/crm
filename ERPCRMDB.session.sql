--@block
ALTER TABLE Accounts
ADD PRIMARY KEY (AccountID),


MODIFY AccountID INT AUTO_INCREMENT,
AUTO_INCREMENT = 10000; --Fix in code

--@block
ALTER TABLE Leads
ADD PRIMARY KEY (LeadID),
ADD FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID)

--@block
ALTER TABLE Orders
ADD PRIMARY KEY (OrderID),
ADD FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID);

--@block
ALTER TABLE OrderDetails
ADD PRIMARY KEY (OrderDetailID),
ADD FOREIGN KEY (OrderID) REFERENCES Orders(OrderID);

--@block
ALTER TABLE SupportTickets
ADD PRIMARY KEY (TicketID),
ADD FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID),
ADD FOREIGN KEY (ContactID) REFERENCES Contacts(ContactID)

--@block
ALTER TABLE Users
ADD PRIMARY KEY (UserID),
MODIFY UserID INT AUTO_INCREMENT,
ADD UNIQUE (Username);

--@block
DELETE FROM Users

