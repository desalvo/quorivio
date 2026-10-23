import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {parseLeaderboardPage} from '../src/pagination-policy.ts';
test('leaderboard page validation rejects ambiguity and overflow',()=>{
 assert.equal(parseLeaderboardPage(undefined),1);
 assert.equal(parseLeaderboardPage('1'),1);
 assert.equal(parseLeaderboardPage('100000'),100000);
 for(const x of ['0','100001','2x','1.5','-3','Infinity','',{},['1']])assert.equal(parseLeaderboardPage(x),null);
});
