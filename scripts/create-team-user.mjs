import { createUser, getUserByEmail } from '/app/node_modules/thepopebot/lib/db/users.js';
import { getDb } from '/app/node_modules/thepopebot/lib/db/index.js';
import { userChannels } from '/app/node_modules/thepopebot/lib/db/schema.js';
import { eq } from '/app/node_modules/drizzle-orm/index.js';
import { randomUUID } from 'crypto';

const email = process.env.CREATE_EMAIL || 'm.khoshlahjeh.azar@gmail.com';
const password = process.env.CREATE_PASSWORD;
const telegramId = process.env.CREATE_TELEGRAM_ID || '262358925';

if (!password) {
  console.error('CREATE_PASSWORD is required');
  process.exit(1);
}

try {
  const existing = getUserByEmail(email);
  if (existing) {
    console.log('User already exists:', existing.email, 'role:', existing.role);
  } else {
    const user = await createUser(email, password, 'user');
    console.log('Created user:', JSON.stringify(user));
  }

  // Link Telegram channel
  const user = getUserByEmail(email);
  if (user) {
    const db = getDb();
    const channels = db.select().from(userChannels).where(eq(userChannels.userId, user.id)).all();
    const existingTelegram = channels.find(c => c.channel === 'telegram');

    if (existingTelegram) {
      console.log('Telegram channel already linked to chat ID:', existingTelegram.channelChatId);
    } else {
      const now = Date.now();
      db.insert(userChannels).values({
        id: randomUUID(),
        userId: user.id,
        channel: 'telegram',
        channelChatId: telegramId,
        verifiedAt: now,
        systemMessagesEnabled: 1,
        createdAt: now,
        updatedAt: now,
      }).run();
      console.log('Linked Telegram ID:', telegramId, 'to user:', email);
    }
  }
  console.log('Done.');
} catch (e) {
  console.error('Error:', e.message);
  process.exit(1);
}
