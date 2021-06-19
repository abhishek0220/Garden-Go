from sqlalchemy.orm import Session
from Garden_Go.Database import models, SessionLocal
import json


def getLeaderboard(db: Session):
    allUserInfo = db.query(models.User).all()
    leaderboard = [[user.email, user.score] for user in allUserInfo]

    leaderboard.sort(key=lambda x:x[1], reverse=True)
    leaderboardResponse = dict(zip([i for i in range(1,len(leaderboard)+1)],[{"userEmail":x[0], "score":x[1]} for x in leaderboard]))
    return json.dumps(leaderboardResponse)

if __name__ == '__main__':
    print(getLeaderboard(SessionLocal()))