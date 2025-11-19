/*
  Warnings:

  - You are about to drop the column `screen_list` on the `users` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "sessions" ADD COLUMN     "screen_list" JSONB;

-- AlterTable
ALTER TABLE "users" DROP COLUMN "screen_list";
