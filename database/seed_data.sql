INSERT INTO author_status (email, book_title, isbn, publishing_status, royalty_status, final_submission_date, book_live_date)
VALUES 
('sara.johnson@xyz.com', 'Whimsical Verses', '978-3-16-148410-0', 'Published', 'Paid', '2024-01-15', '2024-03-01'),
('john.doe@email.com', 'The Silent Poet', '978-1-23-456789-7', 'In Progress', 'Accruing', '2024-02-10', NULL),
('kunal.maurya@example.com', 'Agentic AI Workflows', '978-0-12-345678-9', 'Published', 'Paid', '2023-11-20', '2024-01-05')
ON CONFLICT (email) DO NOTHING;


INSERT INTO author_identities (primary_email, platform, handle_or_id)
VALUES 
('sara.johnson@xyz.com', 'whatsapp', '+91 9876543210'),
('sara.johnson@xyz.com', 'instagram', '@sarapoetry23'),
('john.doe@email.com', 'whatsapp', '+1 555-0123')
ON CONFLICT (platform, handle_or_id) DO NOTHING;
